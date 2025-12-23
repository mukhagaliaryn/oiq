window.MathJax = {
  tex: {
    inlineMath: [['\\(', '\\)'], ['$', '$']],
    displayMath: [['\\[', '\\]'], ['$$', '$$']]
  }
};


document.addEventListener("DOMContentLoaded", () => {
  if (window.MathJax && MathJax.typesetPromise) {
    MathJax.typesetPromise();
  }
});