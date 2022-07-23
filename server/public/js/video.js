const media = document.getElementById('video1');
const media2 = document.getElementById('video2');

var video_state = 0; // 0 - играет BG; 1-играет основное; 2-переход от основного к bg
var video_queue = []
var video_end_command = null

function getTransitionEndEventName() {
  var transitions = {
    "transition": "transitionend",
    "OTransition": "oTransitionEnd",
    "MozTransition": "transitionend",
    "WebkitTransition": "webkitTransitionEnd"
  }
  let bodyStyle = document.body.style;
  for (let transition in transitions) {
    if (bodyStyle[transition] != undefined) {
      return transitions[transition];
    }
  }
}

media.addEventListener(getTransitionEndEventName(), () => {
  if (video_state === 2) {
    video_state = 0
    if (video_queue.length) playMedia(...video_queue.shift())
  }
  console.log('Animation ended', video_state);
});


const play = document.querySelector('.play');

play.addEventListener('click', playMediaStart);
media2.addEventListener('ended', end_play);

function end_play() {
  console.log('end_play', video_end_command)
  if (video_end_command) {
    for (var cmd of video_end_command.split(';')) {
      ws.send(cmd)
    }
  }
  video_state = 2
  media.classList.remove('hide')
}

function playMediaStart() {
  playMedia('media/1.mp4')
}

function playMedia(file, end_command) {
  if (!file) {
    if (video_queue.length) playMedia(...video_queue.shift())
    return
  } else if (video_state !== 0) {
    video_queue.push([file, end_command])
    return
  }
  video_state = 1;
  video_end_command = end_command
  media2.getElementsByTagName('source')[0].src = file
  media2.load()
  media.classList.add('hide');
}

