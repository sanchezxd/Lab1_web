import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg') # Используем бэкенд, не требующий GUI
import matplotlib.pyplot as plt
import os

def process_striped_image(input_path, output_path, direction, width):
    """
    Функция меняет местами соседние полосы изображения.
    """
    img = Image.open(input_path)
    # Преобразуем изображение в массив numpy
    arr = np.array(img)
    new_arr = arr.copy()
    
    if direction == 'horizontal':
        max_h = arr.shape[0]
        for i in range(0, max_h, 2 * width):
            s1_start, s1_end = i, min(i + width, max_h)
            s2_start, s2_end = s1_end, min(s1_end + width, max_h)
            
            h1 = s1_end - s1_start
            h2 = s2_end - s2_start
            
            # Меняем блоки строк (горизонтальные полосы) местами
            if h1 > 0 and h2 > 0:
                new_arr[s1_start : s1_start + h2] = arr[s2_start : s2_end]
                new_arr[s1_start + h2 : s1_start + h2 + h1] = arr[s1_start : s1_end]
                
    elif direction == 'vertical':
        max_w = arr.shape[1]
        for i in range(0, max_w, 2 * width):
            s1_start, s1_end = i, min(i + width, max_w)
            s2_start, s2_end = s1_end, min(s1_end + width, max_w)
            
            w1 = s1_end - s1_start
            w2 = s2_end - s2_start
            
            # Меняем блоки столбцов (вертикальные полосы) местами
            if w1 > 0 and w2 > 0:
                new_arr[:, s1_start : s1_start + w2] = arr[:, s2_start : s2_end]
                new_arr[:, s1_start + w2 : s1_start + w2 + w1] = arr[:, s1_start : s1_end]

    # Сохраняем результат
    out_img = Image.fromarray(new_arr)
    out_img.save(output_path)

def plot_color_distribution(input_path, output_plot_path):
    """
    Строит график распределения цветов (гистограмму) для исходного изображения.
    """
    img = Image.open(input_path).convert('RGB')
    arr = np.array(img)
    
    plt.figure(figsize=(8, 5))
    colors = ('r', 'g', 'b')
    
    for i, color in enumerate(colors):
        hist, bins = np.histogram(arr[:, :, i], bins=256, range=(0, 256))
        plt.plot(bins[:-1], hist, color=color, label=f'Канал {color.upper()}')
        
    plt.title('График распределения цветов (исходное изображение)')
    plt.xlabel('Интенсивность пикселя (0-255)')
    plt.ylabel('Количество пикселей')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig(output_plot_path)
    plt.close()
