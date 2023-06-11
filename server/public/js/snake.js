// const canvas = document.getElementById("game");
const canvas = document.createElement('canvas')
const video = document.getElementById('video')

// Установка размеров канваса на весь экран
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
document.body.appendChild(canvas);

const font = new FontFace("batman", "url(fonts/BatmanForeverAlternativeCyr.woff)", {
  // style: "normal",
  // weight: "400",
  // stretch: "condensed",
});
// wait for font to be loaded
font.load().then(function (font) {
  document.fonts.add(font)
})


const margin = {h: 1, w: 2, t: 2}
const ctx = canvas.getContext("2d");

const ground = new Image();
// ground.src = "img/ground.png";
ground.src = "img/bg.jpg";
let bg = {
  'pos': {'x': 0, 'y': 0},
  'go_pos': {'x': -300, 'y': -300},
  'step': {'dx': -1, 'dy': -1},
}

let active_screen = false

let level = 0
const foot_map = [
  [[18, 4], [26, 6], [21, 16], [18, 5]],//0
  [[18, 4], [26, 16],],//7
  [[18, 4], [26, 16],],//7
  [[18, 4], [26, 16],],//7
  [[18, 4], [26, 16],],//7
  [[18, 4], [26, 16],],//7
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

let box = 36;
let score = 0;

let first_eat = false;
let energy = 0;
let all_level_done = false

const display_size = {
  h: Math.floor(window.innerHeight / box - margin.h - margin.t),
  w: Math.floor(window.innerWidth / box - margin.w * 2),
}

let food = {}

let snake = [];

document.addEventListener("keydown", direction);

let level_hover = -1
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
  console.log(active_screen)
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
        active_screen = 'video'
        setTimeout(reset_level, 5000, true)
      } else {
        inputField.text = ''
      }
      return;
    }
    if (hoverKey.charCodeAt(0) < 100) {
      if (inputField.text.length < 10) inputField.text += hoverKey
    } else {
      inputField.text = inputField.text.substring(0, inputField.text.length - 1)
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

function drawBg() {

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

  ctx.beginPath();
  console.log(display_size.y, 0)
  for (let i = 0; i < display_size.h; i++) {
    ctx.fillText(i, margin.w * box - 13, margin.t * box + box * i + 10);
    if (i === 0) continue

    ctx.moveTo(margin.w * box, margin.t * box + box * i);
    ctx.lineTo(margin.w * box + display_size.w * box, margin.t * box + box * i);
  }
  for (let i = 0; i < display_size.w; i++) {
    ctx.fillText(i, margin.w * box + box * i + 10, margin.w * box - 13, margin.t * box + box * i);
    if (i === 0) continue
    ctx.moveTo(margin.w * box + box * i, margin.t * box);
    ctx.lineTo(margin.w * box + box * i, margin.t * box + display_size.h * box);
  }
  ctx.closePath();
  ctx.stroke();

  ctx.beginPath();
  ctx.shadowColor = 'rgba(255,255,0,1)'; // string Color of the shadow; RGB, RGBA, HSL, HEX, and other inputs are valid.
  ctx.shadowOffsetX = 0; // integerHorizontal distance of the shadow, in relation to the text.
  ctx.shadowOffsetY = 0; // integer Vertical distance of the shadow, in relation to the text.
  ctx.shadowBlur = 15; // integer Blurring effect to the shadow, the larger the value, the greater the blur.
  ctx.strokeStyle = 'rgba(200, 200, 0, 0.5)';
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

function drawRotatedImage(image, x, y, angle) {

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

function drawScaleImage(image, x, y, scale) {

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

function drawGame() {
  active_screen = 'game'
  drawBg()

  // ctx.drawImage(foodImg, (food.x + margin.w) * box, (food.y + margin.t) * box);
  //drawRotatedImage(foodImg, (food.x + margin.w + 0.5) * box, (food.y + margin.t + 0.5) * box, 90);

  drawScaleImage(foodImg, (food.x + margin.w + 0.5) * box, (food.y + margin.t + 0.5) * box,
    .85 + Math.sin((new Date().getTime() % 3600) / 600) * 0.15);

  for (let i = 0; i < snake.length; i++) {
    let is_last = i === snake.length - 1
    let img = i === 0 ? snakeHead : is_last ? snakeHvist : first_eat && !energy ? snakeImgR : snakeImgY
    drawRotatedImage(img,
      (snake[i].x + margin.w + 0.5) * box, (snake[i].y + margin.t + 0.5) * box,
      snake[is_last ? i - 1 : i].alpha)

    // ctx.fillStyle = i === 0 ? "green" : "red";
    // ctx.fillRect((snake[i].x + margin.w) * box, (snake[i].y + margin.t) * box, box, box);
  }

  ctx.fillStyle = "white";
  ctx.font = "50px Arial";
  ctx.fillText(score, box * 2.5, box * 1.7);

  ctx.font = '30px Arial';
  ctx.textBaseline = 'bottom';
  ctx.textAlign = 'center';
  ctx.fillText('level ' + level, box * 2.5, canvas.height);

  let snakeX = snake[0].x;
  let snakeY = snake[0].y;

  if (snakeX === food.x && snakeY === food.y) {
    first_eat = true
    energy = 1
    score++;
    if (!foot_map[level][score]) {
      clearInterval(game);
      level++
      ctx.fillText('next level', 500, 500);
      setTimeout(reset_level, 3000,)
      return
    }
    food = {
      x: foot_map[level][score][0],
      y: foot_map[level][score][1],
    };
  }

  if (next_move < new Date().getTime()) {
    next_move = new Date().getTime() + 200

    if (snake[snake.length - 2].can_remove) snake.pop();


    if (dir === "left") snakeX -= 1;
    if (dir === "right") snakeX += 1;
    if (dir === "up") snakeY -= 1;
    if (dir === "down") snakeY += 1;


    if (snakeX < 0 || snakeX >= display_size.w
      || snakeY < 0 || snakeY >= display_size.h) {
      ctx.fillStyle = "white";
      ctx.font = "50px Arial";
      ctx.fillText('end', 500, 500);
      clearInterval(game);
      setTimeout(reset_level, 3000,)
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

    eatTail(newHead, snake);

    snake.unshift(newHead);
  }
}

// Отрисовка меню
function drawMenu() {
  active_screen = 'menu'
  // ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(ground, bg.pos.x, bg.pos.y);

  ctx.font = '20px Arial';
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';

  let item_width = 350
  let item_height = 70
  let item_margin = 10
  let item_y = (canvas.height - ((item_height + item_margin) * foot_map.length + item_margin)) / 2

  for (let i = 1; i <= foot_map.length; i++) {
    // Отрисовка прямоугольника
    ctx.fillStyle = (i - 1) === level_hover ? 'rgba(255, 255, 255, 0.5)' : 'rgba(255, 255, 255, 1)';
    ctx.fillRect(canvas.width / 2 - item_width / 2, item_y, item_width, item_height);

    // Отрисовка текста
    ctx.fillStyle = 'black';
    ctx.fillText('LEVEL ' + i, canvas.width / 2, item_y + item_height / 2);
    item_y += item_height + item_margin
  }
}

let game
const reset_level = function (go) {
  video.style.display = 'none'
  video.pause()
  canvas.classList.add('no_cursor')
  snake = [
    {x: 4, y: 4, alpha: 0, can_remove: true},
    {x: 3, y: 4, alpha: 0, can_remove: true},
    {x: 2, y: 4, alpha: 0, can_remove: true},
    {x: 1, y: 4, alpha: 0, can_remove: true},
  ];
  dir = 'right';
  first_eat = false
  score = 0
  if (!foot_map[level] || (!go && all_level_done)) {
    all_level_done = true
    canvas.classList.remove('no_cursor')
    game = setInterval(drawMenu, 50);
  } else {
    food = {
      x: foot_map[level][score][0],
      y: foot_map[level][score][1],
    };
    game = setInterval(drawGame, 20);
  }
}


// Определение раскладки клавиатуры
let keyboardLayout = [
  ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', '⟵'],
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
  width: keySize * 4,
  height: keySize,
  text: '',
  label: {
    x: keyboardLayout[0][0].x,
    text: 'введите название проекта',
  }
};

function drawKeyboard() {
  active_screen = 'keyboard'
  ctx.drawImage(ground, bg.pos.x, bg.pos.y);

  ctx.font = '30px batman';
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';

  // Отрисовка клавиш
  for (let row = 0; row < keyboardLayout.length; row++) {
    for (let col = 0; col < keyboardLayout[row].length; col++) {
      ctx.fillStyle = keyboardLayout[row][col].hover ? 'rgba(255, 255, 255, 0.5)' : 'rgba(255, 255, 255, 1)';
      ctx.fillRect(keyboardLayout[row][col].x, keyboardLayout[row][col].y,
        keyboardLayout[row][col].w, keyboardLayout[row][col].h);

      ctx.fillStyle = 'black';
      ctx.fillText(keyboardLayout[row][col].text,
        keyboardLayout[row][col].x + keyboardLayout[row][col].w / 2,
        keyboardLayout[row][col].y + keyboardLayout[row][col].h / 2);
    }
  }

  ctx.textBaseline = 'middle';
  ctx.textAlign = 'left';

  // Отрисовка поля для ввода
  ctx.fillStyle = 'lightgray';
  ctx.fillRect(inputField.x - inputField.width, inputField.y, inputField.width, inputField.height);

  ctx.fillStyle = 'black';
  ctx.fillText(inputField.text, inputField.x + 10 - inputField.width, inputField.y + inputField.height / 2);

  ctx.font = '20px batman';
  ctx.fillText(inputField.label.text.toUpperCase(), inputField.label.x, inputField.y + inputField.height / 2);
}

// reset_level(true)

// game = setInterval(drawMenu, 50);
game = setInterval(drawKeyboard, 50);