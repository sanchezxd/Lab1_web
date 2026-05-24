import os
from flask import Flask, render_template, request
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from image_utils import process_striped_image, plot_color_distribution

app = Flask(__name__)
app.config['SECRET_KEY'] = '2456'

# Настройки для Google reCAPTCHA v2
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdbF_ssAAAAAIRE6L8AAt6VUIxo9DmMubsbkkBz'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdbF_ssAAAAAA-G9osiy6apwROxdu_TEYHMvxwQ'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

Bootstrap(app)

# Форма ввода данных
class ImageForm(FlaskForm):
    upload = FileField('Загрузите исходное изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Допустимы только изображения!')
    ])
    direction = SelectField('Направление чередования', choices=[
        ('horizontal', 'По горизонтали'), 
        ('vertical', 'По вертикали')
    ])
    stripe_width = IntegerField('Ширина полосы (в пикселях)', validators=[
        DataRequired(), 
        NumberRange(min=1, message='Ширина должна быть больше 0')
    ])
    recaptcha = RecaptchaField()
    submit = SubmitField('Обработать изображение')

@app.route("/", methods=['GET', 'POST'])
def index():
    form = ImageForm()
    
    orig_img_url = None
    proc_img_url = None
    plot_img_url = None
    
    if form.validate_on_submit():
        # Обеспечение безопасного имени файла
        filename = secure_filename(form.upload.data.filename)
        
        # Директории сохранения
        input_path = os.path.join('static', 'uploads', filename)
        output_path = os.path.join('static', 'processed', f'striped_{filename}')
        plot_path = os.path.join('static', 'plots', f'hist_{filename}')
        
        # 1. Сохранение исходного изображения
        form.upload.data.save(input_path)
        
        # 2. Обработка изображения (обмен полос)
        process_striped_image(
            input_path, 
            output_path, 
            form.direction.data, 
            form.stripe_width.data
        )
        
        # 3. Построение графика распределения цветов исходного файла
        plot_color_distribution(input_path, plot_path)
        
        # Формирование путей для шаблона
        orig_img_url = f'/{input_path}'
        proc_img_url = f'/{output_path}'
        plot_img_url = f'/{plot_path}'

    return render_template(
        'index.html', 
        form=form,
        orig_img_url=orig_img_url,
        proc_img_url=proc_img_url,
        plot_img_url=plot_img_url
    )

if __name__ == "__main__":
    # Создание необходимых папок при запуске
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/processed', exist_ok=True)
    os.makedirs('static/plots', exist_ok=True)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
