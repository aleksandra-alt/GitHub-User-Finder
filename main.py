import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os


class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("500x600")

        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()

        # Интерфейс
        tk.Label(root, text="Введите логин GitHub:", font=("Arial", 12)).pack(pady=10)

        self.search_entry = tk.Entry(root, font=("Arial", 12), width=30)
        self.search_entry.pack(pady=5)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Найти", command=self.search_user, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="В избранное", command=self.add_to_favorites, width=10).pack(side=tk.LEFT, padx=5)

        # Результаты поиска
        self.info_label = tk.Label(root, text="", font=("Arial", 10), justify=tk.LEFT)
        self.info_label.pack(pady=10)

        # Список избранного
        tk.Label(root, text="Избранные пользователи:", font=("Arial", 10, "bold")).pack(pady=5)
        self.fav_listbox = tk.Listbox(root, width=50, height=10)
        self.fav_listbox.pack(pady=5, padx=10)

        self.update_fav_listbox()

        self.current_user_data = None

    def search_user(self):
        username = self.search_entry.get().strip()

        # Валидация: поле не должно быть пустым
        if not username:
            messagebox.showwarning("Ошибка", "Поле поиска не должно быть пустым!")
            return

        try:
            response = requests.get(f"https://github.com{username}")
            if response.status_code == 200:
                data = response.json()
                self.current_user_data = {
                    "login": data.get("login"),
                    "name": data.get("name"),
                    "url": data.get("html_url")
                }
                display_text = f"Логин: {data.get('login')}\nИмя: {data.get('name')}\nURL: {data.get('html_url')}"
                self.info_label.config(text=display_text, fg="black")
            else:
                self.info_label.config(text="Пользователь не найден", fg="red")
                self.current_user_data = None
        except Exception as e:
            messagebox.showerror("Ошибка сети", f"Не удалось подключиться к API: {e}")

    def add_to_favorites(self):
        if not self.current_user_data:
            messagebox.showwarning("Внимание", "Сначала найдите пользователя!")
            return

        login = self.current_user_data["login"]
        if any(user['login'] == login for user in self.favorites):
            messagebox.showinfo("Инфо", "Пользователь уже в избранном")
            return

        self.favorites.append(self.current_user_data)
        self.save_favorites()
        self.update_fav_listbox()
        messagebox.showinfo("Успех", f"{login} добавлен в избранное!")

    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            with open(self.favorites_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_favorites(self):
        with open(self.favorites_file, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, indent=4, ensure_ascii=False)

    def update_fav_listbox(self):
        self.fav_listbox.delete(0, tk.END)
        for user in self.favorites:
            self.fav_listbox.insert(tk.END, f"{user['login']} ({user.get('name') or 'No name'})")


if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
