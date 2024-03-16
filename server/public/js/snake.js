var base_url = (location.protocol || 'http:') + '//' + location.hostname + (location.port != 80 ? ':' + location.port : '');
var ws = false;
var ws_timer = false;
var animationEnd = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
var ws_error = 0
var hard_level = 2
var snake_interval = [300, 200, 100]

document.addEventListener("DOMContentLoaded", function (event) {
  ws_start();
});

var app = {}

function set_active_screen(screen) {
  active_screen = screen
  document.body.setAttribute('screen', screen)
  ws_send('screen', screen)
}

let game_status = 0 // 0 - base game, 1 - locked, 2 - catalog

function ws_start() {
  if (ws) {
    ws.close();
    ws.onclose = function () {
    };
    ws.onopen = function () {
    };
    ws.onerror = function () {
    };
    ws.onmessage = function () {
    };
    if (ws.terminate) ws.terminate()
    console.log('kill ws')
  }

  ws = new WebSocket(base_url.replace('http', 'ws'))
  clearInterval(ws_timer);
  ws_timer = setInterval(ws_start, 2000);

  ws.onopen = function () {
    console.log('WebSocket Connect');
    clearInterval(ws_timer);
  };

  ws.onerror = function (error) {
    console.log('WebSocket Error ', error);
    ws_error++
    if (ws_error > 600) ws_error = 600
    clearInterval(ws_timer);
    ws_timer = setInterval(ws_start, 1000 + ws_error * 100);
  };

  ws.onclose = function () {
    console.log('WebSocket connection closed');
    ws_error++
    if (ws_error > 600) ws_error = 600
    clearInterval(ws_timer);
    ws_timer = setInterval(ws_start, 1000 + ws_error * 100);
  };

  ws.onmessage = function (e) {
    var data = e.data.split(':')
    var key = data.shift()
    data = data.join(':')
    console.log(key, data)
    if (typeof (app) !== 'undefined') {
      if (key === 'time') {
        app.time = data
        return
      }

      console.log(key, data)

      if (key === 'esp_list') {
        app.esp_list = JSON.parse(data)
        return
      }

      if (key === 'snake') {
        let cmd = data.split(':')
        if (cmd[0] === 'hard_level') {
          hard_level = parseInt(cmd[1])
          return
        }
        return
      }

      if (key === 'game') {
        app.game = JSON.parse(data)
        if (app.game['lang']) t_lang = app.game['lang']
        return
      }

      if (key === 'game_time') {
        app.game_time = data
        return
      }
      if (key === 'status') {
        app.status = JSON.parse(data)
        if (app.status['logo'] && app.status['logo']['finish'] && game_status === 0) {
          game_status = 1
          if (game) {
            clearInterval(game)
          }
          set_active_screen('locked')
        }
        return
      }
    }
  }
}

function ws_send(key, data) {
  if (ws.readyState !== 1) return
  let msg = '?snake:' + key + ':' + data
  if (ws) ws.send(msg)
}

let box = 42;
let score = 0;

let first_eat = false;
let energy = 0;
let all_level_done = false

// Настройки стилей кнопки
const fillColor = 'rgba(14,28,39,0.78)'; // Синий цвет заливки
const hoverColor = 'rgba(14,28,39,1)'; // Синий цвет заливки
const borderColor = '#86DAFF'; // цвет рамки
const textColor = '#fff'; // Белый цвет текста
const borderRadius = 10; // Радиус скругления углов
const borderWidth = 3; // Толщина рамки

let t_lang = 'ru'
const lang_dict = {
  'ru': {
    'select_level': "Выберите уровень:",
    'level': "Уровень",
    'product_name': 'Название проекта:',
  },
  'en': {
    'select_level': "Select level:",
    'level': "Level",
    'product_name': 'Product name:',
  },
  'ua': {
    'select_level': "Виберіть рівень:",
    'level': "Рівень",
    'product_name': 'Назва проекту:',
  }
}

// const canvas = document.getElementById("game");
const canvas = document.createElement('canvas')
const video = document.getElementById('video')

// Установка размеров канваса на весь экран
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
document.body.appendChild(canvas);

const font = new FontFace("batman", "url(fonts/BatmanForeverAlternativeCyr.woff)", {});
font.load().then(function (font) {
  document.fonts.add(font)
})


const margin = {h: 1, w: 2, t: 2}
const ctx = canvas.getContext("2d");

const ground = new Image();
// ground.src = "img/ground.png";
// ground.src = "img/bg.jpg";
ground.src = "img/Fon2.jpg";
let bg = {
  'pos': {'x': 0, 'y': 0},
  'go_pos': {'x': -300, 'y': -300},
  'step': {'dx': -1, 'dy': -1},
}

let active_screen = false

let level = 0
let max_level = 0
const foot_map = [
  [[15, 3], [25, 6], [21, 18], [15, 15], [15, 4]],//0
  [[15, 3], [25, 6], [20, 10], [15, 15], [25, 18]],//2
  [[25, 3], [15, 5], [19, 10], [25, 15], [15, 18]],//5
  [[15, 6], [20, 3], [25, 8], [25, 18]],//7
]

const foodImg = new Image();
foodImg.src = "img/food.png";
const snakeHead = new Image();
snakeHead.src = 'img/golova_zmii.png'
const snakeHvist = new Image();
snakeHvist.src = 'img/hvist_zmii.png'
const snakeImgY = new Image();
snakeImgY.src = 'img/tilo_yellow_zmii.png'
const snakeImgR = new Image();
snakeImgR.src = 'img/tilo_red_zmii.png'


const display_size = {
  h: Math.floor(window.innerHeight / box - margin.h - margin.t),
  w: Math.floor(window.innerWidth / box - margin.w * 2),
}

let food = {}

let snake = [];

document.addEventListener("keydown", direction);

let level_hover = -1

function drawButton(params) {
  const {x, y, h, w, hover, text} = params;

  // ctx.clearRect(x, y, w, h); // Очищаем область кнопки

  // Определение цвета заливки в зависимости от состояния наведения
  const buttonFillColor = hover ? hoverColor : fillColor;

  if (hover) {
    ctx.shadowColor = borderColor; // string Color of the shadow; RGB, RGBA, HSL, HEX, and other inputs are valid.
    ctx.shadowOffsetX = 0; // integerHorizontal distance of the shadow, in relation to the text.
    ctx.shadowOffsetY = 0; // integer Vertical distance of the shadow, in relation to the text.
    ctx.shadowBlur = 15; // integer Blurring effect to the shadow, the larger the value, the greater the blur.
  }
  // Нарисовать прямоугольник кнопки
  ctx.fillStyle = buttonFillColor;
  ctx.strokeStyle = borderColor;
  ctx.lineWidth = borderWidth;
  ctx.beginPath();
  ctx.moveTo(x + borderRadius, y);
  ctx.lineTo(x + w - borderRadius, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + borderRadius);
  ctx.lineTo(x + w, y + h - borderRadius);
  ctx.quadraticCurveTo(x + w, y + h, x + w - borderRadius, y + h);
  ctx.lineTo(x + borderRadius, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - borderRadius);
  ctx.lineTo(x, y + borderRadius);
  ctx.quadraticCurveTo(x, y, x + borderRadius, y);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();

  ctx.font = '55px batman';
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';

  // Выводим текст на кнопке
  ctx.fillStyle = textColor;
  ctx.fillText(text, x + w / 2 + 2, y + h / 2 + 4);
  ctx.shadowBlur = 0
}

function drawInput({x, y, h, w, label, text}) {
  x = x - w

  // Нарисовать прямоугольник кнопки
  ctx.fillStyle = fillColor;
  ctx.strokeStyle = borderColor;
  ctx.lineWidth = borderWidth;
  ctx.beginPath();
  ctx.moveTo(x + borderRadius, y);
  ctx.lineTo(x + w - borderRadius, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + borderRadius);
  ctx.lineTo(x + w, y + h - borderRadius);
  ctx.quadraticCurveTo(x + w, y + h, x + w - borderRadius, y + h);
  ctx.lineTo(x + borderRadius, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - borderRadius);
  ctx.lineTo(x, y + borderRadius);
  ctx.quadraticCurveTo(x, y, x + borderRadius, y);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();


  // Написать текст
  ctx.fillStyle = '#fff'; // Белый цвет текста
  ctx.font = '40px batman';
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'left';
  ctx.fillText(text, x + 20, y + h / 2);

  ctx.fillStyle = '#fff';
  ctx.font = '35px batman';
  ctx.fillText(lang_dict[t_lang][inputField.label.text].toUpperCase(), label.x, y + h / 2);
}

canvas.addEventListener('mousemove', function (event) {
  const x = event.clientX - canvas.offsetLeft;
  const y = event.clientY - canvas.offsetTop;

  let item_width = 350
  let item_height = 70
  let item_margin = 10
  let item_y = (canvas.height - ((item_height + item_margin) * foot_map.length + item_margin)) / 2

  if ((x < canvas.width / 2 - item_width / 2) || (x > canvas.width / 2 + item_width / 2)) {
    level_hover = -1
    return
  }

  let y_ = y - item_y
  if (y_ < 0) {
    level_hover = -1
  }
  y_ = y_ / (item_height + item_margin)
  if (y_ > foot_map.length) {
    level_hover = -1
    return;
  }
  level_hover = Math.floor(y_)
  if (y_ - level_hover > item_height / (item_height + item_margin)) {
    level_hover = -1
    return;
  }
});

let hoverKey = null
canvas.addEventListener('mousemove', function (event) {
  const x = event.clientX - canvas.offsetLeft;
  const y = event.clientY - canvas.offsetTop;
  hoverKey = null
  for (let row = 0; row < keyboardLayout.length; row++) {
    for (let col = 0; col < keyboardLayout[row].length; col++) {
      keyboardLayout[row][col].hover = (
        (keyboardLayout[row][col].x < x) &&
        (keyboardLayout[row][col].x > x - keyboardLayout[row][col].w) &&
        (keyboardLayout[row][col].y < y) &&
        (keyboardLayout[row][col].y > y - keyboardLayout[row][col].h))
      if (keyboardLayout[row][col].hover) hoverKey = keyboardLayout[row][col].text
    }
  }
});

canvas.addEventListener('mousedown', function (event) {
  if (active_screen === 'menu') {
    if (level_hover === -1) return
    level = level_hover
    clearInterval(game)
    setTimeout(reset_level, 300, true)
    return;
  }

  if (active_screen === 'keyboard') {
    if (hoverKey === null) return
    if (hoverKey.length > 3) {
      if (inputField.text === 'UROBOROS') {
        clearInterval(game)
        video.currentTime = 0
        video.style.display = 'block'
        video.play()
        set_active_screen('video')
        ws_send('pass_ok', 1)
        setTimeout(reset_level, 5000, true)
      } else {
        ws_send('login_pre', inputField.text)
        ws_send('login', '')
        ws_send('pass_ok', 0)
        inputField.text = ''
      }
      return;
    }
    if (hoverKey.charCodeAt(0) < 91 && hoverKey.charCodeAt(0) > 63) {
      if (inputField.text.length < 8) inputField.text += hoverKey

      let textWidth = ctx.measureText(inputField.text).width; // Измеряем ширину текста
      while (textWidth > inputField.w - 10 && inputField.text.length > 0) {
        inputField.text = inputField.text.slice(0, -1); // Обрезаем последний символ
        textWidth = ctx.measureText(inputField.text).width; // Измеряем ширину текста с многоточием
      }
      ws_send('login', inputField.text)
    } else {
      inputField.text = inputField.text.substring(0, inputField.text.length - 1)
      ws_send('login', inputField.text)
    }
  }
})

let dir;

function direction(event) {
  if (first_eat && !energy) return;

  const new_dir = {
    37: "left",
    38: "up",
    39: "right",
    40: "down"
  }[event.keyCode]
  const conflict_dir = {
    "right": "left",
    "down": "up",
    "left": "right",
    "up": "down"
  }[dir]

  if (new_dir && dir !== new_dir && conflict_dir !== new_dir) {
    if (first_eat) energy = 0
    dir = new_dir
  }
}

function eatTail(head, arr) {
  for (let i = 0; i < arr.length; i++) {
    if (head.x === arr[i].x && head.y === arr[i].y) {
      clearInterval(game);
      setTimeout(reset_level, 2000,)
    }
  }
}

function drawBg(ctx) {

  /*if (bg.pos.x !== bg.go_pos.x) {
    bg.pos.x += bg.step.dx
    bg.pos.y += bg.step.dy
  }*/
  ctx.drawImage(ground, bg.pos.x, bg.pos.y);

  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.fillRect(margin.w * box, margin.t * box, display_size.w * box, display_size.h * box);

  ctx.strokeStyle = 'rgba(255,255,255,0.27)';
  ctx.lineWidth = 2;

  ctx.fillStyle = "white";
  ctx.font = "16px Arial";

  ctx.textBaseline = 'middle';
  ctx.textAlign = 'right';

  ctx.beginPath();
  // console.log(display_size.y, 0)
  for (let i = 1; i < display_size.h; i++) {
    // ctx.fillText(i, margin.w * box - 13, margin.t * box + box * i + 10);
    // if (i === 0) continue

    ctx.moveTo(margin.w * box, margin.t * box + box * i);
    ctx.lineTo(margin.w * box + display_size.w * box, margin.t * box + box * i);
  }
  for (let i = 1; i < display_size.w; i++) {
    // ctx.fillText(i, margin.w * box + box * i + 10, margin.w * box - 13, margin.t * box + box * i);
    // if (i === 0) continue
    ctx.moveTo(margin.w * box + box * i, margin.t * box);
    ctx.lineTo(margin.w * box + box * i, margin.t * box + display_size.h * box);
  }
  ctx.closePath();
  ctx.stroke();

  ctx.beginPath();
  ctx.shadowColor = '#fff101'; // string Color of the shadow; RGB, RGBA, HSL, HEX, and other inputs are valid.
  ctx.shadowOffsetX = 0; // integerHorizontal distance of the shadow, in relation to the text.
  ctx.shadowOffsetY = 0; // integer Vertical distance of the shadow, in relation to the text.
  ctx.shadowBlur = 15; // integer Blurring effect to the shadow, the larger the value, the greater the blur.
  ctx.strokeStyle = '#fff101';
  ctx.lineWidth = 4;
  ctx.moveTo(margin.w * box, margin.t * box);
  ctx.lineTo(margin.w * box, (margin.t + display_size.h) * box);
  ctx.lineTo((margin.w + display_size.w) * box, (margin.t + display_size.h) * box);
  ctx.lineTo((margin.w + display_size.w) * box, margin.t * box);
  ctx.lineTo(margin.w * box, margin.t * box);
  ctx.closePath();
  ctx.stroke();
  ctx.shadowBlur = 0;
}

const TO_RADIANS = Math.PI / 180

function drawRotatedImage(ctx, image, x, y, angle) {

  // save the current co-ordinate system
  // before we screw with it
  ctx.save();

  // move to the middle of where we want to draw our image
  ctx.translate(x, y);

  // rotate around that point, converting our
  // angle from degrees to radians
  ctx.rotate(angle * TO_RADIANS);

  // draw it up and to the left by half the width
  // and height of the image
  ctx.drawImage(image, -(image.width / 2), -(image.height / 2));

  // and restore the co-ords to how they were when we began
  ctx.restore();
}

function drawScaleImage(ctx, image, x, y, scale) {

  // save the current co-ordinate system
  // before we screw with it
  ctx.save();

  // move to the middle of where we want to draw our image
  ctx.translate(x, y);

  // rotate around that point, converting our
  // angle from degrees to radians
  ctx.scale(scale, scale);

  // draw it up and to the left by half the width
  // and height of the image
  ctx.drawImage(image, -(image.width / 2), -(image.height / 2));

  // and restore the co-ords to how they were when we began
  ctx.restore();
}

let next_move = 0;

function drawDynamicIndication(ctx) {
  let pos = {x: box * 2, y: box * 1.5, w: box * display_size.w}
  // ctx.fillStyle = "white";
  // ctx.textBaseline = 'bottom';
  // ctx.textAlign = 'left';
  // ctx.font = "50px batman";
  // ctx.fillText('score', box * 2, box * 1.5);

  // ctx.beginPath();
  // ctx.rect(20, 20, 150, 100);
  // ctx.stroke();

  ctx.strokeStyle = '#fff';
  ctx.fillStyle = "white";
  let ts = Math.floor(new Date().getTime() / 500) / 3;
  for (let i = 0; i < 25; i++) {
    ctx.beginPath();
    let h = Math.abs(Math.sin(ts + i * 0.5) * 0.5 + Math.cos((ts + i * 0.5) * 1.8) * 0.5 - Math.sin((ts + i * 0.5) * 2.8) * 0.5)
    ctx.fillRect(pos.x, pos.y, 4, -box * h * 0.8);
    ctx.stroke();
    pos.x += 12
  }

  pos.x += 1000

  let w = pos.w - pos.x + margin.w * box

  for (let i = 0; i < 3; i++) {
    ctx.beginPath();
    let wk = Math.abs(Math.sin(ts + i * 0.5) * 0.5 +
      Math.cos((ts + i * 0.5) * 1.8) * 0.5 - Math.sin((ts + i * 0.5) * 2.8) * 0.5)
    if (wk > 1) wk = 1
    ctx.fillRect(pos.x, pos.y, w * wk * 0.8, -4);
    ctx.stroke();
    pos.y -= 12
  }
}

let ctx_bg = null
let m_canvas = null

function init_game() {
  set_active_screen('game')
  m_canvas = document.createElement('canvas')
  m_canvas.width = canvas.width;
  m_canvas.height = canvas.height;
  ctx_bg = m_canvas.getContext("2d");

  drawBg(ctx_bg)
  drawStaticIndication(ctx_bg)
}

function drawStaticIndication(ctx) {
  let pos = {x: box * 2 + 350, y: box * 1.5, w: box * display_size.w}

  ctx.textAlign = 'left';
  ctx.textBaseline = 'bottom';
  ctx.font = "40px batman";
  ctx.strokeStyle = '#fff';
  let text = 'TE88697-4T. 56T/NYUR 5679-456'
  ctx.fillText(text, pos.x, pos.y + box * 0.2)

  pos = {x: box * margin.w, y: canvas.height - box}
  // треугольники белые
  ctx.strokeStyle = '#fff';
  let dy = -box * 0.2
  for (let i = 0; i < 4; i++) {
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y + dy);
    ctx.lineTo(pos.x + box * 0.3, pos.y + box * 0.3 + dy);
    ctx.lineTo(pos.x + box * 0.6, pos.y + dy);
    ctx.closePath();
    ctx.stroke();
    pos.x += box * 1
  }
  pos.x += margin.w * box

  ctx.font = '40px batman';
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'left';
  text = lang_dict[t_lang]['level'] + ' ' + (level + 1)
  ctx.fillText(text, pos.x, pos.y + box * 0.2)
  pos.x += 60 + ctx.measureText(text).width

  text = 'MITMN567-567-567/6M7.676.689'
  ctx.textAlign = 'right';
  pos.x = (display_size.w + margin.w) * box
  ctx.fillText(text, pos.x, pos.y + box * 0.2)

}

function drawGame() {
  let tmp_canvas = document.createElement('canvas')
  tmp_canvas.width = canvas.width;
  tmp_canvas.height = canvas.height;
  let tmp_ctx = tmp_canvas.getContext("2d");
  tmp_ctx.drawImage(m_canvas, 0, 0);

  // ctx.drawImage(foodImg, (food.x + margin.w) * box, (food.y + margin.t) * box);
  //drawRotatedImage(tmp_ctx, foodImg, (food.x + margin.w + 0.5) * box, (food.y + margin.t + 0.5) * box, 90);

  drawScaleImage(tmp_ctx, foodImg, (food.x + margin.w + 0.5) * box, (food.y + margin.t + 0.5) * box,
    .85 + Math.sin((new Date().getTime() % 3600) / 600) * 0.15);

  for (let i = 0; i < snake.length; i++) {
    let is_last = i === snake.length - 1
    let img = i === 0 ? snakeHead : is_last ? snakeHvist : first_eat && !energy ? snakeImgR : snakeImgY
    drawRotatedImage(tmp_ctx, img,
      (snake[i].x + margin.w + 0.5) * box, (snake[i].y + margin.t + 0.5) * box,
      snake[is_last ? i - 1 : i].alpha)

    // ctx.fillStyle = i === 0 ? "green" : "red";
    // ctx.fillRect((snake[i].x + margin.w) * box, (snake[i].y + margin.t) * box, box, box);
  }

  drawDynamicIndication(tmp_ctx)

  let snakeX = snake[0].x;
  let snakeY = snake[0].y;

  if (snakeX === food.x && snakeY === food.y) {
    first_eat = true
    energy = 1
    score++;
    ws_send('foods', score)
    if (!foot_map[level][score]) {
      clearInterval(game);
      level++
      // ctx.fillText('next level', 500, 500);
      setTimeout(reset_level, 1000,)
      return
    }
    food = {
      x: foot_map[level][score][0],
      y: foot_map[level][score][1],
    };
  }

//  if (next_move < new Date().getTime()) {
//    next_move = next_move + tact_render

  if (snake[snake.length - 2].can_remove) snake.pop();


  if (dir === "left") snakeX -= 1;
  if (dir === "right") snakeX += 1;
  if (dir === "up") snakeY -= 1;
  if (dir === "down") snakeY += 1;


  if (snakeX < 0 || snakeX >= display_size.w
    || snakeY < 0 || snakeY >= display_size.h) {
    // ctx.fillStyle = "white";
    // ctx.font = "50px Arial";
    // ctx.fillText('end', 500, 500);
    clearInterval(game);
    setTimeout(reset_level, 1500,)
  }

  let alpha_head = {
    "left": 180,
    "up": 270,
    "right": 0,
    "down": 90,
  }[dir]

  let newHead = {
    x: snakeX,
    y: snakeY,
    alpha: alpha_head,
    can_remove: !first_eat
  };

  ctx.drawImage(tmp_canvas, 0, 0);

  eatTail(newHead, snake);

  snake.unshift(newHead);
//  }
}

// Отрисовка меню
function drawMenu() {
  set_active_screen('menu')
  // ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(ground, bg.pos.x, bg.pos.y);

  ctx.font = '20px Arial';
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';

  let item_width = 450
  let item_height = 70
  let item_margin = 20
  let item_y = (canvas.height - ((item_height + item_margin) * (foot_map.length + 1) + item_margin)) / 2

  ctx.font = '55px batman';
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';

  // Выводим текст на кнопке
  ctx.fillStyle = textColor;
  ctx.fillText(lang_dict[t_lang]['select_level'], canvas.width / 2, item_y);
  item_y += item_height + item_margin

  for (let i = 1; i <= foot_map.length; i++) {
    drawButton({
      x: canvas.width / 2 - item_width / 2,
      y: item_y,
      h: item_height,
      w: item_width,
      hover: (i - 1) === level_hover,
      text: lang_dict[t_lang]['level'] + ' ' + i
    })

    item_y += item_height + item_margin
  }
}

let game
const reset_level = function (go) {
  video.style.display = 'none'
  video.pause()
  canvas.classList.add('no_cursor')
  if (game) {
    if (max_level < level) {
      max_level = level
      ws_send('level', level)
    }
    clearInterval(game)
  }
  next_move = new Date().getTime() + snake_interval[hard_level - 1]
  let start_y = foot_map[0][0][1]
  snake = [
    {x: 4, y: start_y, alpha: 0, can_remove: true},
    {x: 3, y: start_y, alpha: 0, can_remove: true},
    {x: 2, y: start_y, alpha: 0, can_remove: true},
    {x: 1, y: start_y, alpha: 0, can_remove: true},
  ];
  dir = 'right';
  first_eat = false
  score = 0
  ws_send('foods', score)
  if (!foot_map[level] || (!go && all_level_done)) {
    all_level_done = true
    setTimeout(ws_send, 500, 'finish', 1)
    canvas.classList.remove('no_cursor')
    game = setInterval(drawMenu, 100);
  } else {
    food = {
      x: foot_map[level][score][0],
      y: foot_map[level][score][1],
    };
    ws_send('level_now', level + 1)
    init_game()
    game = setInterval(drawGame, snake_interval[hard_level - 1]);
  }
}


// Определение раскладки клавиатуры
let keyboardLayout = [
  ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', '<'],
  ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
  ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'O', 'P'],
  ['Enter']
];

// Определение параметров клавиш
const keySize = 80; // Размер клавиш
const keyMargin = 10; // Отступ между клавишами
const keyMarginTop = 10 + (canvas.height - keyboardLayout.length * (keySize + keyMargin) - keyMargin) / 2; // Отступ Сверху

for (let row = 0; row < keyboardLayout.length; row++) {
  let keySizeLine = keyboardLayout[row].length > 3 ? keySize : keySize * 5 + keyMargin * 4
  let marginLeft = (canvas.width - (keyboardLayout[row].length * (keySizeLine + keyMargin) - keyMargin)) / 2
  let lineLayout = []
  let marginTop = keyboardLayout[row].length > 3 ? 0 : keySize + keyMargin
  for (let col = 0; col < keyboardLayout[row].length; col++) {
    const keyX = marginLeft + col * (keySize + keyMargin) + keyMargin;
    const keyY = keyMarginTop + marginTop + row * (keySize + keyMargin) + 2 * keyMargin;

    lineLayout.push({
      'text': keyboardLayout[row][col],
      'x': keyX,
      'y': keyY,
      'h': keySize,
      'w': keySizeLine,
      'hover': false,
    })
  }
  keyboardLayout[row] = lineLayout
}

// Параметры поля для ввода
const inputField = {
  x: keyboardLayout[0][keyboardLayout[0].length - 1].x + keySize,
  y: keyMarginTop - keySize * 2,
  w: keySize * 4,
  h: keySize,
  text: '',
  label: {
    x: keyboardLayout[0][0].x,
    text: 'product_name',
  }
};

function drawKeyboard() {
  set_active_screen('keyboard')
  ctx.drawImage(ground, bg.pos.x, bg.pos.y);


  const {x, y, w, h} = {
    x: inputField.label.x - keySize * 1.5,
    y: inputField.y - keySize,
    w: inputField.x - inputField.label.x + keySize * 3,
    h: keyboardLayout[keyboardLayout.length - 1][0].y + keySize * 3 - inputField.y
  }

  ctx.fillStyle = 'rgba(5, 5, 5, 0.2)'
  ctx.strokeStyle = borderColor;
  ctx.lineWidth = borderWidth;
  ctx.beginPath();
  ctx.moveTo(x + borderRadius, y);
  ctx.lineTo(x + w - borderRadius, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + borderRadius);
  ctx.lineTo(x + w, y + h - borderRadius);
  ctx.quadraticCurveTo(x + w, y + h, x + w - borderRadius, y + h);
  ctx.lineTo(x + borderRadius, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - borderRadius);
  ctx.lineTo(x, y + borderRadius);
  ctx.quadraticCurveTo(x, y, x + borderRadius, y);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(x, y + h * 0.2);
  ctx.lineTo(0, y + h * 0.2);
  ctx.moveTo(x, y + h * 0.65);
  ctx.lineTo(0, y + h * 0.65);
  ctx.moveTo(x, y + h * 0.85);
  ctx.lineTo(0, y + h * 0.85);

  ctx.moveTo(x + w, y + h * 0.35);
  ctx.lineTo(canvas.width, y + h * 0.35);
  ctx.moveTo(x + w, y + h * 0.55);
  ctx.lineTo(canvas.width, y + h * 0.55);
  ctx.closePath()
  ctx.stroke()


  ctx.font = '30px batman';
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';

  // Отрисовка клавиш
  for (let row = 0; row < keyboardLayout.length; row++) {
    for (let col = 0; col < keyboardLayout[row].length; col++) {
      drawButton(keyboardLayout[row][col])
    }
  }

  drawInput(inputField)
}

// reset_level(true)

// game = setInterval(drawMenu, 50);
game = setInterval(drawKeyboard, 50);

setTimeout(ws_send, 500, 'hard_level', hard_level)
setTimeout(ws_send, 500, 'pass_ok', 0)
setTimeout(ws_send, 500, 'level', 0)
setTimeout(ws_send, 500, 'foods', 0)
setTimeout(ws_send, 500, 'finish', 0)