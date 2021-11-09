function main() {
  const renders = ['portrait', 'face', 'skin'];
  const options = ['player_name', 'skin_url', 'skin_file'];
  for (i in renders) {
    const render = renders[i]
    var div = document.createElement('div');
    div.id = render;
    div.classList.add('render');
    var text_div = document.createElement('div');
    text_div.classList.add('text');
    var label = document.createElement('label');
    label.innerText = 'https://skindentity.deta.dev/'+render+'/?';
    var select = document.createElement('select');
    select.onchange = function() {switchInput(this)};
    for (e in options) {
        const opt = options[e];
        var option = document.createElement('option');
        option.value = opt;
        option.innerHTML = opt;
        select.appendChild(option);
    };
    var label_two = document.createElement('label');
    label_two.innerText = '=';
    var input = document.createElement('input');
    input.onchange = function() {updateImage(this)};
    input.type = 'minecraft_player';
    input.placeholder = 'Steve';
    var button = document.createElement('button');
    button.innerText = "Copy";
    button.onclick = function() {navigator.clipboard.writeText(urlFromInputs(this.parentElement));};
    var img = document.createElement('img');
    img.src = 'previews/' + render + '.png';
    img.alt = 'previews/' + render + '.png';
    img.onerror = async function() {this.src = 'previews/' + render + '.png'};

    text_div.appendChild(label);
    text_div.appendChild(select);
    text_div.appendChild(label_two);
    text_div.appendChild(input);
    div.appendChild(button);
    div.appendChild(text_div);
    div.appendChild(img);

    document.getElementById('container').appendChild(div);
  }
}

function updateImage(element) {
  const div = element.parentElement;
  var img = div.parentElement.getElementsByTagName('img')[0];
  img.src = urlFromInputs(div);
}

function switchInput(element) {
  const div = element.parentElement;
  const option = element.value;
  var input = div.getElementsByTagName('input')[0];
  switch(option) {
    case 'player_name':
      input.type = 'minecraft_player';
      input.placeholder = 'Steve';
      input.onchange = function() { updateImage(this); };
    break;
    case 'skin_url':
      input.type = 'minecraft_skin_url';
      input.placeholder = 'http://assets.mojang.com/SkinTemplates/steve.png';
      input.onchange = function() { updateImage(this); };
    break;
    case 'skin_file':
      input.type = 'file';
      input.placeholder = null;
      input.onchange = function() {
        base64(this);
        updateImage(this);
      };
    break;
  }
}

async function urlFromInputs(div) {
  const main = div.getElementsByTagName('label')[0].innerText;
  const api = div.getElementsByTagName('select')[0].value;
  const value = div.getElementsByTagName('input')[0].value;
  // add more here later
  console.log(main + api + '=' + value);
  return main + api + '=' + value;
}

async function base64(element) {
  var file = element.files[0];
  var reader = new FileReader();
  reader.onload = function() {
    element.value = reader.result.replace(/^data:.+;base64,/, '');
  }
  reader.readAsDataURL(file);
}