from django.db import models


# Create your models here.
class Speaker(models.Model):
    telegram_id = models.IntegerField(
        verbose_name='Телеграм-ID докладчика'
    )
    fullname = models.CharField(
        max_length=100,
        help_text='Введите имя и фамилию докладчика',
        verbose_name='Имя и фамилия выступающего'
    )
    speciality = models.CharField(
        max_length=1000,
        help_text='Введите специальность',
        verbose_name='Специальность докладчика',
    )

    def __str__(self):
        return f'{self.fullname}'

    class Meta:
        verbose_name = 'докладчика'
        verbose_name_plural = 'Выступающие'


class Conference(models.Model):
    name = models.CharField(
        max_length=500,
        help_text='Название конференции',
        verbose_name='Название конференции',
    )
    date = models.DateField(
        help_text='Дата конференции',
        verbose_name='Дата конференции',
    )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'конференцию'
        verbose_name_plural = 'Конференции'


class Performance(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название выступления'
    )
    description = models.TextField(
        max_length=5000,
        verbose_name='Описание выступления'
    )
    time = models.TimeField(
        help_text='Введите время выступления',
        verbose_name='Время выступления',
    )
    speaker = models.ForeignKey(
        to=Speaker,
        on_delete=models.CASCADE,
        related_name='performances',
        verbose_name='Выступающий',
        null=True
    )
    conference = models.ForeignKey(
        to=Conference,
        on_delete=models.CASCADE,
        related_name='performances',
        verbose_name='На какой конференции будет выступление',
        null=True
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'выступление'
        verbose_name_plural = 'Выступления'


class Question(models.Model):
    telegram_user_id = models.IntegerField(
        verbose_name='Телеграм-ID задающего вопрос'
    )
    speaker = models.ForeignKey(
        to=Speaker,
        on_delete=models.CASCADE,
        verbose_name='Выступающий'
    )
    question = models.TextField(
        verbose_name='Вопрос'
    )

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'Вопросы'
