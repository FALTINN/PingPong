from typing import List, Tuple, Dict
from random import randint
import pygame
import sys

# КОНСТАНТЫ
display_size = 900, 600
platform_speed = 5
platform_size = (15, 100)
ball_speed = 5
ball_size = (25, 25)
ball_max_speed = 10
ball_extra_speed_mult = 0.1



class App:
    # КОНСТАНТЫ
    KEY_PRESSED = 2     # Клавиша нажата
    KEY_HOLD = 1        # Клавиша зажата
    KEY_RELEASED = 0    # Клавиша отпущена

    def __init__(self):
        pygame.init()  # Инициализация pygame

        # Переменные
        self.is_running = True  # Работает ли наша программа
        self.keys = dict()      # Состояния клавиш клавиатуры
        self.fps = 60           # Желаемое количество кадров в секунду
        self.ticks = 0

        # Создаём и настраиваем окно игры
        pygame.display.set_caption('PING-PONG')     # Изменяем назание окна
        flags = pygame.RESIZABLE | pygame.SCALED    # Флаги окна
        self.display = pygame.display.set_mode(display_size, flags)  # Создайм окно

        # Время и текст
        self.clock = pygame.time.Clock()
        self.score_font = pygame.font.Font(None, 45)
        self.font = pygame.font.Font(None, 30)

        # Игровые объекты
        self.ball = Ball(
            self, tuple(map(lambda x: x/2, display_size)),randint(0, 360),
            ball_speed, ball_max_speed, ball_extra_speed_mult
        )
        self.platforms = [
            Platform((50, 300), {'up': pygame.K_w, 'down': pygame.K_s}),
            Platform((850, 300), {'up': pygame.K_UP, 'down': pygame.K_DOWN})
        ]

        # Задний фон
        self.background = pygame.Surface(display_size)
        pygame.draw.rect(
            self.background, (255, 255, 255),
            [(display_size[0]/2 - 1, 0), (2, display_size[1])]
        )
        pygame.draw.circle(
            self.background, (255, 255, 255), list(map(lambda x: x/2, display_size)), max(ball_size) + 2
        )
        pygame.draw.circle(
            self.background, (0, 0, 0), list(map(lambda x: x/2, display_size)), max(ball_size)
        )

    def run(self):
        ''' Главный цикл игры '''

        while self.is_running:
            self.hendler_events()   # Обрабатываем нажатия клавиш
            self.update_objects()   # Обновляем объекты
            self.redraw()           # Перерисовываем все объекты

            self.ticks += 1
            self.clock.tick(self.fps)  # Поддерживаем желаемую частоту кадров

    def hendler_events(self):
        ''' Отлавливаем и записываем все нажатия клавиш '''

        # Обработка уже записанных клавиш
        for key in self.keys.copy():                # Перебираем все события
            if self.keys[key] == self.KEY_PRESSED:      # Если состояние клавиши - нажата
                self.keys[key] = self.KEY_HOLD          # Состояние клавиши меняется на зажата 
            elif self.keys[key] == self.KEY_RELEASED:   # Если состояние клавиши - отпущена
                self.keys.pop(key)                      # Клавиша удаляется из словаря

        # Обработка новых событий
        for event in pygame.event.get():    # Перебираем все события
            if event.type == pygame.QUIT:   # Если пользователь пытается закрыть программу
                self.is_running = False     # Программа пересаёт работать

            elif event.type == pygame.KEYDOWN:          # Если клавиша была нажата
                self.keys[event.key] = self.KEY_PRESSED # Запоминаем эту клавишу
                if event.key == pygame.K_ESCAPE:        # Если была нажата клавиша ESCAPE
                    self.is_running = False             # Программа пересаёт работать

            elif event.type == pygame.KEYUP:                # Если клавиша была отпущена
                self.keys[event.key] = self.KEY_RELEASED    # Изменяем состояние клавиши на отпущена

    def update_objects(self):
        ''' Обновляем все объекты '''
        self.ball.update()
        for platform in self.platforms:
            platform.update(self.keys)

    def redraw(self):
        ''' Перерисовываем все объекты '''

        self.display.blit(self.background, (0, 0))  # Закрашиваем предыдущий кадр
        self.ball.render(self.display)              # Отрисовываем мячик
        for platform in self.platforms:             # Перебираем все плотформы
            platform.render(self.display)           # Отрисовываем их

        # Отрисовываем частоту кадров
        text = 'FPS: ' + str( round(self.clock.get_fps(), 2) )  # Получаем частоту кадров
        self.display.blit(self.font.render(text, True, (255, 255, 255)), (10, 10))  # Отображаем результат

        # Отрисовываем очки игроков
        text = ' - '.join(
            list(map(lambda x: str(x.score), self.platforms))  # Очки игроков -> текст
        )
        image_text = self.score_font.render(text, True, (255, 255, 255))
        text_rect = image_text.get_rect(centerx=display_size[0]/2, top=10)
        self.display.blit(image_text, text_rect)  # Отображаем результат

        # Отображаем изменения
        pygame.display.update()

    def restart(self):
        self.ball.restart()
        for platform in self.platforms:
            platform.restart()



class Platform:
    ''' Платформа, которой будет управлять игрок '''

    def __init__(self,
            position: List[float],  # Начальная позиция
            keys: Dict[str, int],   # Словарь, где ключи - строки 'up' и 'down', а значения - клавиши, зажав которые игрок заставит двигаться платформу
            speed: float = platform_speed,      # Скорость движения платформы
            _size: Tuple[int] = platform_size   # Размер платформы
            ):

        # Создаём картинку
        self.image = pygame.Surface(_size)  # Создаём поверхность
        self.image.set_colorkey((0, 0, 0))  # Задаём прозрачный цвет
        pygame.draw.rect(self.image, (255, 255, 255), [(0, 0), _size], 0, 7)  # Рисуем прямоугольник с закруглёнными краями

        self.start_position = list(position)  # Стартовая позиция платформы
        self.position = list(position)  # Позиция платформы
        self.speed = speed              # Скорость передвижения
        self.score = 0
        self.keys = keys                # Ключи управления платформой

    @property
    def rect(self) -> pygame.Rect:
        ''' Возвращает прямоугольник в которой вписана картинка '''
        return self.image.get_rect(center=self.position)

    def update(self, keys):
        ''' Обновление платформы '''

        # Передвигаем платформу
        if self.keys['up'] in keys:         # Если нажата/зажата/отпущена клавиша вверх
            self.position[1] -= self.speed  # Сдвигаем платформу вверх
        if self.keys['down'] in keys:       # Если нажата/зажата/отпущена клавиша вниз
            self.position[1] += self.speed  # Сдвигаем платформу вниз

        tempRect = self.rect
        if tempRect.top < 0:
            tempRect.top = 0
            self.position[0] = tempRect.centerx
        elif tempRect.bottom > display_size[1]:
            tempRect.bottom = display_size[1]
            self.position[1] = tempRect.centery

    def render(self, surface: pygame.Surface):
        ''' Отрисовка картинки '''
        surface.blit(self.image, self.rect)

    def restart(self):
        self.position = self.start_position.copy()



class Ball:
    ''' Класс мяча '''

    def __init__(self, 
            app: App,                       # Класс игры
            position: List[float],          # Начальная позиция мяча
            vector_rotate: float,           # Поворот вектора, в направлении которого будет происходить движение
            speed: float,                   # Скорость мяча
            max_speed: float,               # Максимальная скорость
            extra_speed_mult: float,        # На сколько будет увеличиваться скорость за каждый тик игры
            _size: Tuple[int] = ball_size   # Размер мяча
            ):

        # Создаём картинку
        self.image = pygame.Surface(_size)  # Создаём поверхность
        self.image.set_colorkey((0, 0, 0))  # Задаём прозрачный цвет
        pygame.draw.circle(self.image, (255, 0, 0), (_size[0]/2, _size[1]/2), min(_size)/2)  # Рисуем окружность

        self.start_position = list(position)  # Стартовая позиция платформы
        self.position = list(position)  # Позиция мяча
        self.vector = pygame.math.Vector2((0, -1)).rotate(vector_rotate)   # Вектор движения
        self.extra_speed_mult = extra_speed_mult    # На сколько будет увеличиваться скорость за каждый тик игры
        self.max_speed = max_speed  # Максимальная скорость
        self.start_speed = speed    # Начальная скорость
        self.app = app  # Экземпляр главного класса игры

    @property
    def rect(self) -> pygame.Rect:
        ''' Возвращает прямоугольник в которой вписана картинка '''
        return self.image.get_rect(center=self.position)

    def update(self):
        ''' Обновление мяча '''

        # Получаем сдвиг по осям Х и У
        extra_speed = self.app.ticks * self.extra_speed_mult        # Высчитывваем дополнительную скорость
        speed = min(self.start_speed + extra_speed, self.max_speed) # Выбираем минимум
        motion = (self.vector * speed).xy                           # Высчитываем сдвиг

        # Сдвиг по оси Х
        self.position[0] += motion[0]   # Двигаем по Х
        temp_rect = self.rect           # Прямоугольник, в которой вписан мяч
        for platform in self.app.platforms:
            self.check_collision(platform, temp_rect, (motion[0], 0))   # Проверяем на столкновения с платформами

        # Сдвиг по оси У
        self.position[1] += motion[1]   # Двигаем по У
        temp_rect = self.rect           # Прямоугольник, в которой вписан мяч
        for platform in self.app.platforms:
            self.check_collision(platform, temp_rect, (0, motion[1]))   # Проверяем на столкновения с платформами

        # Проверка на столкновения с границами экрана
        temp_rect = self.rect   # Прямоугольник, в которой вписан мяч
        if temp_rect.top < 0:   # Если касаемся верхней границы экрана
            self.vector.reflect_ip(pygame.math.Vector2(0, 1))
            temp_rect.top = 0
            self.position[1] = temp_rect.centery
        elif temp_rect.bottom > self.app.display.get_height():  # Если касаемся нижней границы экрана
            self.vector.reflect_ip(pygame.math.Vector2(0, 1))
            temp_rect.bottom = self.app.display.get_height()
            self.position[1] = temp_rect.centery

        if temp_rect.left < 0:  # Если касаемся левой границы экрана
            self.app.platforms[0].score += 1
            self.app.restart()
        elif temp_rect.right > self.app.display.get_width():    # Если касаемся правой границы экрана
            self.app.platforms[1].score += 1
            self.app.restart()

    def check_collision(self,
            platform: Platform,     # Платформа
            rect: pygame.Rect,      # Прмяоугольник, в которой вписан мяч
            motion: Tuple[float]    # Сдвиг
            ):

        # Если прямоугольник мяча касается прямоугольника платформы
        if rect.colliderect(platform.rect):
            # Проверка по оси Х
            if motion[0] > 0:   # Если мяч двигается вправо
                rect.right = platform.rect.left                     # Сдивгаем мяч до границы платформы
                self.vector.reflect_ip(pygame.math.Vector2(1, 0))   # Отражаем вектор движения
                self.position[0] = rect.centerx                     # Изменяем координаты
            elif motion[0] < 0: # Если мяч двигается влево
                rect.left = platform.rect.right                     # Сдивгаем мяч до границы платформы
                self.vector.reflect_ip(pygame.math.Vector2(1, 0))   # Отражаем вектор движения
                self.position[0] = rect.centerx                     # Изменяем координаты

            # Проверка по оси У
            if motion[1] > 0:   # Если мяч двигается ввкрх
                rect.bottom = platform.rect.top                     # Сдивгаем мяч до границы платформы
                self.vector.reflect_ip(pygame.math.Vector2(0, 1))   # Отражаем вектор движения
                self.position[1] = rect.centery                     # Изменяем координаты
            elif motion[1] < 0: # Если мяч двигается вниз
                rect.top = platform.rect.bottom                     # Сдивгаем мяч до границы платформы
                self.vector.reflect_ip(pygame.math.Vector2(0, 1))   # Отражаем вектор движения
                self.position[1] = rect.centery                     # Изменяем координаты

            # Немного изменяем вектор движения мяча
            self.vector.rotate_ip(randint(0, 20) - 10)

    def render(self, surface: pygame.Surface):
        ''' Отрисовка картинки '''
        surface.blit(self.image, self.rect)

    def restart(self):
        self.position = self.start_position.copy()
        self.vector.rotate_ip(randint(0, 360))



if __name__ == '__main__':
    app = App()

    try:
        app.run()
    except KeyboardInterrupt:
        pass

    pygame.quit()
    sys.exit()
