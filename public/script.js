/*
let fileInput = document.createElement('input')
fileInput.id = 'input'
fileInput.type = 'file'
fileInput.onchange = function() {
  base64(this)
  updateImage(this)
}
*/
window.onload = function() {
  var optionSelector = document.getElementById('optionSelector')
  switchInput(optionSelector)
  updateImage(optionSelector)
}

function switchInput(element) {
  const option = element.value
  var parent = element.parentElement
  var input = parent.querySelector('input')
  switch(option) {
    case 'name':
      input.type = "minecraft_username"
      input.placeholder = 'MHF_Steve'
      break
    case 'uuid':
      input.type = "minecraft_player_uuid"
      input.placeholder = 'c06f89064c8a49119c29ea1dbd1aab82'
      break
    case 'blob':
      input.type = "minecraft_player_blob"
      input.placeholder = 'ewogICJ0aW1lc3RhbXAiIDogMTY4MjM2MjQxNjQ0MywKICAicHJvZmlsZUlkIiA6ICJjMDZmODkwNjRjOGE0OTExOWMyOWVhMWRiZDFhYWI4MiIsCiAgInByb2ZpbGVOYW1lIiA6ICJNSEZfU3RldmUiLAogICJ0ZXh0dXJlcyIgOiB7CiAgICAiU0tJTiIgOiB7CiAgICAgICJ1cmwiIDogImh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMzFmNDc3ZWIxYTdiZWVlNjMxYzJjYTY0ZDA2ZjhmNjhmYTkzYTMzODZkMDQ0NTJhYjI3ZjQzYWNkZjFiNjBjYiIKICAgIH0KICB9Cn0'
      break
    case 'url':
      input.type = "minecraft_skin_url"
      input.placeholder = 'http://assets.mojang.com/SkinTemplates/steve.png'
      break
  }
}

// arguments

let additionalArguments = [
  'slim',
  'overlay',
  'margin',
  'upscale',
]
let argumentCount = 0

function addArgument(element) {

  var parent = element.parentElement
  var text = parent.querySelector('#text')
  var template = parent.querySelector('#argumentTemplate')
  copy = template.content.cloneNode(true)

  if (argumentCount > 0) {
    copy.querySelector('label').innerText = '&'
  }

  argumentCount++
  if (argumentCount >= additionalArguments.length) {
    element.remove()
  }

  text.appendChild(copy)

  var allArgs = text.querySelectorAll('.templateContainer')
  var arg = allArgs[allArgs.length-1]

  switchArgument(arg.querySelector('select'))

}

function switchArgument(element) {
  const option = element.value
  var parent = element.parentElement
  var input = parent.querySelector('input')
  console.log(option)

  switch(option) {
    case 'margin':
      input.type = 'number'
      input.min = 1
      input.max = 8
      break
    case 'upscale':
      input.type = 'number'
      input.min = 2
      input.max = 8
    case 'slim', 'overlay':
      input.type = 'checkbox'
      break
  }

}

// util

function updateImage(element) {
  let div = element.parentElement
  let parent = div.parentElement

  /*
  if (!parent.querySelector('#input').value) {
    return
  }
  */

  let img = parent.querySelector('img')
  let url = textFromElements(div)

  var errorBox = div.parentElement.querySelector('#errorBox')
  errorBox.innerHTML = ''
  img.src = 'public/static/loading.gif'

  console.log('URL:' + url)

  fetch(url, { method: 'GET', headers: {Accept: 'application/json' } }).then(function (response) {

    if (response.status == 441) {
      response.json().then(data =>
        errorBox.innerHTML = data.detail
      )
      return
    }

    response.blob().then(response =>
      img.src = URL.createObjectURL(response)
    )

  });
}

function textFromElements(container) {
  url = ''
  for (const child of container.children) {
    if (child.tagName == 'LABEL') url += child.innerHTML
    else if (child.type == 'checkbox') url += child.checked
    else if (child.tagName == 'DIV') url += textFromElements(child)
    else if (child.value) url += child.value
    else if (child.placeholder) url += encodeURIComponent(child.placeholder)
  }
  return url.replace('&amp;', '&')
}

async function base64(element) {
  var file = element.files[0]
  var reader = new FileReader()
  reader.onload = function() {
    element.value = reader.result.replace(/^data:.+base64,/, '')
  }
  reader.readAsDataURL(file)
}

const escapeHtml = (unsafe) => {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}