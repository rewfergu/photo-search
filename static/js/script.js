const uploadBtn = document.getElementById('upload');
const photoField = document.getElementById('photo');
// const photoSearch = document.getElementById('photoSearchForm');

const image = document.getElementById('imageFile');
const imageTitle = document.getElementById('imageTitle');
const imageDesc = document.getElementById('imageDescription');
const loading = document.getElementById('loadingWindow');

const infoWindow = document.getElementById('overlay');
const closeBtn = document.getElementById('close');

const canvasElement = document.getElementById('canvas');
const ctx = canvasElement.getContext('2d');

let formData;
let request;

uploadBtn.addEventListener('click', () => {
  photoField.click();
});

photoField.addEventListener('change', () => {
  formData = new FormData();
  request = new XMLHttpRequest();
  const reader = new FileReader();

  loading.classList.add('active');

  reader.onload = function(e) {
    const img = new Image();

    img.onload = () => {
      const maxWidth = 640;
      const maxHeight = 480;
      let width = img.width;
      let height = img.height;

      if (width > height) {
        if (width > maxWidth) {
          height *= maxWidth / width;
          width = maxWidth;
        }
      } else {
        if (height > maxHeight) {
          width *= maxHeight / height;
          height = maxHeight;
        }
      }

      canvasElement.width = width;
      canvasElement.height = height;
      ctx.drawImage(img, 0, 0, width, height);

      formData.append('photo', canvasElement.toDataURL('image/png'));
      request.open('POST', '/submitphoto');
      request.send(formData);
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(photoField.files[0]);

  request.upload.addEventListener('loadstart', () => {
    document.getElementById('loadingStatus').innerHTML = 'Sending Image...';
  });

  request.upload.addEventListener('loadend', () => {
    document.getElementById('loadingStatus').innerHTML = 'Searching Database...';
  });

  // Call a function when the state changes.
  request.onreadystatechange = () => {
    if (request.readyState === XMLHttpRequest.DONE && request.status === 200) {
      console.log('success', request.response);
      const response = JSON.parse(request.response);

      if (response.path) {
        image.setAttribute('src', response.path);
        image.classList.remove('hidden');
      }

      if (response.title) {
        imageTitle.innerHTML = response.title;
        imageTitle.classList.remove('hidden');
      }

      if (response.date && response.date !== 'date') {
        document.getElementById('imageDate').innerHTML = response.date;
      }

      if (response.location) {
        document.getElementById('imageLocation').innerHTML = response.location;
      }

      imageDesc.innerHTML = response.description;

      loading.classList.remove('active');
      infoWindow.classList.add('active');
    }
  };
});

closeBtn.addEventListener('click', () => {
  infoWindow.classList.remove('active');
});
