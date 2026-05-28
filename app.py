import os
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template, request
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = '2456'

# Настройка Google reCAPTCHA
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdtsgAtAAAAAMUBXsJ6j3JuiMnOrFZc2Ri25pWx'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdtsgAtAAAAABdaPu0kcZHCYerWVrgk61jvplD2'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

bootstrap = Bootstrap(app)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class ImageProcessingForm(FlaskForm):
    upload = FileField('Загрузите изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения формата JPG, PNG, JPEG!')
    ])
    direction = SelectField('Направление полос', choices=[('vertical', 'Вертикальные'), ('horizontal', 'Горизонтальные')])
    stripe_width = IntegerField('Ширина полосы в пикселях', validators=[DataRequired(), NumberRange(min=1, max=500)])
    recaptcha = RecaptchaField()
    submit = SubmitField('Обработать')

def swap_stripes(filepath, direction, stripe_width):
    img = Image.open(filepath)
    arr = np.array(img)
    
    if direction == 'vertical':
        num_stripes = arr.shape[1] // stripe_width
        for i in range(0, num_stripes - 1, 2):
            start1 = i * stripe_width
            end1 = start1 + stripe_width
            start2 = (i + 1) * stripe_width
            end2 = start2 + stripe_width
            
            temp = arr[:, start1:end1].copy()
            arr[:, start1:end1] = arr[:, start2:end2]
            arr[:, start2:end2] = temp
    elif direction == 'horizontal':
        num_stripes = arr.shape[0] // stripe_width
        for i in range(0, num_stripes - 1, 2):
            start1 = i * stripe_width
            end1 = start1 + stripe_width
            start2 = (i + 1) * stripe_width
            end2 = start2 + stripe_width
            
            temp = arr[start1:end1, :].copy()
            arr[start1:end1, :] = arr[start2:end2, :]
            arr[start2:end2, :] = temp
            
    return Image.fromarray(arr)

def plot_color_distribution(filepath, out_filename):
    img = Image.open(filepath).convert('RGB')
    arr = np.array(img)
    colors = ('r', 'g', 'b')
    
    plt.figure(figsize=(6, 4))
    plt.title('Распределение цветов исходного изображения')
    plt.xlabel('Интенсивность')
    plt.ylabel('Количество пикселей')
    
    for i, color in enumerate(colors):
        hist, bins = np.histogram(arr[:, :, i].ravel(), bins=256, range=(0, 256))
        plt.plot(hist, color=color, alpha=0.7)
        
    plt.tight_layout()
    plot_path = os.path.join(UPLOAD_FOLDER, out_filename)
    plt.savefig(plot_path)
    plt.close()
    return plot_path

@app.route("/", methods=['GET', 'POST'])
def index():
    form = ImageProcessingForm()
    original_img = None
    processed_img = None
    plot_img = None

    if form.validate_on_submit():
        file = form.upload.data
        filename = secure_filename(file.filename)
        
        orig_filename = f"orig_{filename}"
        proc_filename = f"proc_{filename}"
        plot_filename = f"plot_{filename}"
        
        orig_path = os.path.join(UPLOAD_FOLDER, orig_filename)
        proc_path = os.path.join(UPLOAD_FOLDER, proc_filename)
        
        file.save(orig_path)
        
        # Построение графика исходного изображения
        plot_color_distribution(orig_path, plot_filename)
        
        # Обработка изображения
        result_image = swap_stripes(orig_path, form.direction.data, form.stripe_width.data)
        result_image.save(proc_path)
        
        original_img = orig_filename
        processed_img = proc_filename
        plot_img = plot_filename

    return render_template('index.html', form=form, 
                           original_img=original_img, 
                           processed_img=processed_img, 
                           plot_img=plot_img)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
