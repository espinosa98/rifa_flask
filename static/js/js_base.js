window.onload = function() {
  var overlay = document.getElementById('overlay');
  overlay.style.opacity = '0';

setTimeout(function() {
    overlay.style.display = 'none';
  }, 400); // 500ms para dar tiempo a la transición antes de ocultar la capa
};

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function() {
            var submitButton = form.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            setTimeout(function() {
                submitButton.disabled = false;
            }, 3000);
        });
    });
});

document.addEventListener('submit', function(event) {
    var overlay = document.getElementById('overlay');
    overlay.style.display = 'flex';
    overlay.style.opacity = '1';
});