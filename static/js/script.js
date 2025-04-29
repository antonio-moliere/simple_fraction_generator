// Puedes mover el script de mostrar/ocultar solución de index.html aquí
// si planeas añadir más interactividad.

// document.addEventListener('DOMContentLoaded', (event) => {
//     const showSolutionBtn = document.getElementById('show-solution-btn');
//     const solutionDiv = document.getElementById('solution');

     if (showSolutionBtn && solutionDiv) {
         showSolutionBtn.addEventListener('click', function() {
             if (solutionDiv.style.display === 'none') {
                 solutionDiv.style.display = 'block';
                 this.textContent = 'Ocultar Solución';
             } else {
                 solutionDiv.style.display = 'none';
                 this.textContent = 'Mostrar Solución';
             }
         });
     }
 });
