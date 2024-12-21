import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkinter import ttk
import json
import matplotlib.pyplot as plt

class Filter:
    """Абстрактный класс для фильтров"""
    def __init__(self, next_filter=None):
        self.next_filter = next_filter

    def filter_water(self, water):
        if self.next_filter:
            return self.next_filter.filter_water(water)
        return water

    def get_parameters(self):
        return {}

class SedimentFilter(Filter):
    """Фильтр для удаления крупных частиц"""
    def __init__(self, efficiency=50, next_filter=None):
        super().__init__(next_filter)
        self.efficiency = efficiency

    def filter_water(self, water):
        water['sediment'] = max(0, water['sediment'] - self.efficiency)
        return super().filter_water(water)

    def get_parameters(self):
        return {'Тип': 'Седиментный', 'Эффективность': self.efficiency}

class CarbonFilter(Filter):
    """Угольный фильтр для удаления запахов и химикатов"""
    def __init__(self, efficiency=30, next_filter=None):
        super().__init__(next_filter)
        self.efficiency = efficiency

    def filter_water(self, water):
        water['chemicals'] = max(0, water['chemicals'] - self.efficiency)
        return super().filter_water(water)

    def get_parameters(self):
        return {'Тип': 'Угольный', 'Эффективность': self.efficiency}

class ReverseOsmosisFilter(Filter):
    """Фильтр обратного осмоса для удаления мелких частиц"""
    def __init__(self, efficiency=90, next_filter=None):
        super().__init__(next_filter)
        self.efficiency = efficiency

    def filter_water(self, water):
        water['microbes'] = max(0, water['microbes'] - self.efficiency)
        return super().filter_water(water)

    def get_parameters(self):
        return {'Тип': 'Обратный осмос', 'Эффективность': self.efficiency}

class WaterPurificationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система очистки воды")

        self.initial_water = {
            'sediment': 100,
            'chemicals': 100,
            'microbes': 100
        }

        self.filters_chain = None

        self.create_widgets()

    def create_widgets(self):
        # Кнопки управления
        self.start_button = tk.Button(self.root, text="Начать фильтрацию", command=self.start_filtration)
        self.start_button.pack(pady=5)

        self.filter_type_label = tk.Label(self.root, text="Выберите тип фильтра:")
        self.filter_type_label.pack(pady=5)

        self.filter_type_combobox = ttk.Combobox(self.root, values=["Седиментный", "Угольный", "Обратный осмос"])
        self.filter_type_combobox.pack(pady=5)

        self.efficiency_label = tk.Label(self.root, text="Введите эффективность фильтра (0-100):")
        self.efficiency_label.pack(pady=5)

        self.efficiency_entry = tk.Entry(self.root)
        self.efficiency_entry.pack(pady=5)

        self.add_filter_button = tk.Button(self.root, text="Добавить фильтр", command=self.add_filter)
        self.add_filter_button.pack(pady=5)

        self.info_button = tk.Button(self.root, text="Информация о фильтрах", command=self.show_filters_info)
        self.info_button.pack(pady=5)

        self.save_button = tk.Button(self.root, text="Сохранить конфигурацию", command=self.save_configuration)
        self.save_button.pack(pady=5)

        self.load_button = tk.Button(self.root, text="Загрузить конфигурацию", command=self.load_configuration)
        self.load_button.pack(pady=5)

        self.plot_button = tk.Button(self.root, text="Показать график", command=self.plot_results)
        self.plot_button.pack(pady=5)

        # Метка для отображения результата
        self.result_label = tk.Label(self.root, text="")
        self.result_label.pack(pady=10)

        # Текстовое поле для отображения фильтров
        self.filters_text = tk.Text(self.root, height=10, width=50)
        self.filters_text.pack(pady=10)

    def start_filtration(self):
        final_water = self.simulate_water_filtering(self.filters_chain, self.initial_water)
        result_text = f"Конечные параметры воды:\nСедимент: {final_water['sediment']}\nХимикаты: {final_water['chemicals']}\nМикробы: {final_water['microbes']}"
        self.result_label.config(text=result_text)

    def add_filter(self):
        filter_type = self.filter_type_combobox.get()
        try:
            efficiency = int(self.efficiency_entry.get())
            if efficiency < 0 or efficiency > 100:
                raise ValueError("Эффективность должна быть в диапазоне 0-100.")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            return

        if filter_type == "Седиментный":
            self.filters_chain = self.add_filter_stage(self.filters_chain, SedimentFilter(efficiency))
        elif filter_type == "Угольный":
            self.filters_chain = self.add_filter_stage(self.filters_chain, CarbonFilter(efficiency))
        elif filter_type == "Обратный осмос":
            self.filters_chain = self.add_filter_stage(self.filters_chain, ReverseOsmosisFilter(efficiency))
        else:
            messagebox.showerror("Ошибка", "Неизвестный тип фильтра.")

        self.update_filters_display()

    def add_filter_stage(self, chain, new_filter):
        """Добавляет новый фильтр в цепочку"""
        if chain is None:
            return new_filter
        current = chain
        while current.next_filter is not None:
            current = current.next_filter
        current.next_filter = new_filter
        return chain

    def simulate_water_filtering(self, filters_chain, initial_water):
        """Запускает процесс фильтрации воды"""
        final_water = filters_chain.filter_water(initial_water)
        return final_water

    def update_filters_display(self):
        """Обновляет текстовое поле с информацией о фильтрах"""
        self.filters_text.delete(1.0, tk.END)  # Очистка текстового поля
        current = self.filters_chain
        if current is None:
            self.filters_text.insert(tk.END, "Фильтры не добавлены.")
            return
        filters_info = []
        while current is not None:
            filters_info.append(current.get_parameters())
            current = current.next_filter
        filters_text = "\n".join([f"Тип: {info['Тип']}, Эффективность: {info['Эффективность']}" for info in filters_info])
        self.filters_text.insert(tk.END, filters_text)

    def show_filters_info(self):
        """Показывает информацию о фильтрах"""
        info = "Доступные фильтры:\n\n"
        info += "1. Седиментный фильтр: Удаляет крупные частицы. Эффективность: 0-100.\n"
        info += "2. Угольный фильтр: Удаляет запахи и химикаты. Эффективность: 0-100.\n"
        info += "3. Фильтр обратного осмоса: Удаляет мелкие частицы и микроорганизмы. Эффективность: 0-100.\n"
        messagebox.showinfo("Информация о фильтрах", info)

    def save_configuration(self):
        filters_info = []
        current = self.filters_chain
        while current is not None:
            filters_info.append(current.get_parameters())
            current = current.next_filter
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(filters_info, file)
            messagebox.showinfo("Сохранение", "Конфигурация сохранена.")

    def load_configuration(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as file:
                filters_info = json.load(file)
                self.filters_chain = None
                for filter_data in filters_info:
                    if filter_data['Тип'] == 'Седиментный':
                        self.filters_chain = self.add_filter_stage(self.filters_chain, SedimentFilter(filter_data['Эффективность']))
                    elif filter_data['Тип'] == 'Угольный':
                        self.filters_chain = self.add_filter_stage(self.filters_chain, CarbonFilter(filter_data['Эффективность']))
                    elif filter_data['Тип'] == 'Обратный осмос':
                        self.filters_chain = self.add_filter_stage(self.filters_chain, ReverseOsmosisFilter(filter_data['Эффективность']))
            self.update_filters_display()
            messagebox.showinfo("Загрузка", "Конфигурация загружена.")

    def plot_results(self):
        if not self.filters_chain:
            messagebox.showerror("Ошибка", "Не добавлены фильтры для отображения графика.")
            return

        sediment_levels = []
        chemical_levels = []
        microbe_levels = []

        current_water = self.initial_water.copy()
        sediment_levels.append(current_water['sediment'])
        chemical_levels.append(current_water['chemicals'])
        microbe_levels.append(current_water['microbes'])

        current = self.filters_chain
        while current is not None:
            current_water = current.filter_water(current_water)
            sediment_levels.append(current_water['sediment'])
            chemical_levels.append(current_water['chemicals'])
            microbe_levels.append(current_water['microbes'])
            current = current.next_filter

        plt.figure(figsize=(10, 6))
        plt.plot(sediment_levels, label='Седимент', marker='o')
        plt.plot(chemical_levels, label='Химикаты', marker='o')
        plt.plot(microbe_levels, label='Микробы', marker='o')
        plt.title('Изменение параметров воды в процессе фильтрации')
        plt.xlabel('Этап фильтрации')
        plt.ylabel('Уровень загрязнения')
        plt.xticks(range(len(sediment_levels)), [f'Этап {i}' for i in range(len(sediment_levels))])
        plt.legend()
        plt.grid()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = WaterPurificationApp(root)
    root.mainloop()

