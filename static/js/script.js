const toggleBtn2 = document.getElementById("toggleBtn2");
const titleBox = document.getElementById("titleBox1");
const squares = document.querySelectorAll(".squares")
window.addEventListener('load', reveal);
window.addEventListener('scroll', reveal);
const hamburger = document.getElementById('hamburger');
const elements_navbar = document.getElementById('elements_navbar');

hamburger.addEventListener('click', () => {
  elements_navbar.classList.toggle('activeE');
});

squares.forEach(square => {
  square.addEventListener('mousemove', (e) => {
    const rect = square.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width /2
    const centerY = rect.height /2

    const rotateY = ((x - centerX) / centerX) * 25;
    const rotatex = ((y - centerY) / centerY) * 25;

    square.style.transform = `rotateX(${rotatex}deg) rotateY(${rotateY}deg)`;
  });

  square.addEventListener('mouseleave', () => {
    square.style.transform = `rotateX(0deg) rotateY(0deg)`;
  });
});

document.addEventListener("DOMContentLoaded", () => {

  document.getElementById("fileInput").addEventListener("change", () => {
    const file = document.getElementById("fileInput");
    const selectedFileName = document.getElementById("selectedFileName");

    if(file.files.length > 0){
      selectedFileName.textContent = `Archivo seleccionado: ${file.files[0].name}`;
      selectedFileName.style.display = "flex";
    }else{
      selectedFileName.textContent = "";
    }
  });

  document.getElementById("fileInput").addEventListener("change", () => {
  const file = document.getElementById("fileInput");
  const selectedFileName = document.getElementById("selectedFileName");

  if(file.files.length > 0){
    selectedFileName.textContent = `Archivo seleccionado: ${file.files[0].name}`;
    selectedFileName.style.display = "flex";
    selectedFileName.style.justifyContent = "center";
  }else{
    selectedFileName.textContent = "";
  }
});
});

toggleBtn2.addEventListener("click", () => {
  titleBox.classList.toggle("active");
});

function reveal(){
  const reveals = document.querySelectorAll('.reveal');
  const windowHeight = window.innerHeight;
  const revealPoint = 150;

  reveals.forEach(el => {
    const revealTop = el.getBoundingClientRect().top;
    const revealBottom = el.getBoundingClientRect().bottom;

    if(revealTop < windowHeight - revealPoint && revealBottom > 0){
      el.classList.add("active2");
    }else{
      el.classList.remove("active2");
    }
  });
}

function moveTitle(direccion) {
  const rect = titleBox.getBoundingClientRect();
  const currentLeft = rect.left;
  const currentTop = rect.top;

  if (window.innerWidth <= 767) {
    if (direccion === "right") {
      titleBox.style.top = ( 0.45 * window.innerHeight) + "px";
      titleBox.innerHTML = `
        <div id="logInForm">
          <div><h1>Log in</h1></div>
          <div>
            <form method="POST" action='/login'>
              <p>User name:</p>
              <input name="UserName" type="text" placeholder="Name user" required>
              <p>Password:</p>
              <input type="password" name="password" placeholder="Password" required>
              <div id="logInButton"><button type="submit">Log in</button></div>
            </form>
          </div>
        </div>
      `;
    }
    return; 
  }

  if (direccion === "right") {
    titleBox.style.left = (currentLeft + 0.023 * window.innerWidth) + "px";
    titleBox.innerHTML = `
      <div id="logInForm">
        <div><h1>Log in</h1></div>
        <div>
          <form method="POST" action='/login'>
            <p>User name:</p>
            <input name="UserName" type="text" placeholder="Name user" required>
            <p>Password:</p>
            <input type="password" name="password" placeholder="Password" required>
            <div id="logInButton"><button type="submit">Log in</button></div>
          </form>
        </div>
      </div>
    `;
  }
}


function dragOverHandler(event){
  event.preventDefault();
  document.getElementById("file").style.background = "#e3f2fd";
}

function dropHandler(event){
  event.preventDefault();
  const files = event.dataTransfer.files;
  if (files.length > 0) {
    document.getElementById("fileInput").files = files;
    document.getElementById("selectedFileName").textContent = `Selected file: ${files[0].name}`;
    document.getElementById("selectedFileName").style.display = "block";
  }
  document.getElementById("file").style.background = "#f9f9f9";
}


