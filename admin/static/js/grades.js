// Dynamically control the set up of grade and streams.
var gradeSelect = document.getElementById('grade-select')
var streamsSelect = document.querySelector('.hidden-display')
var submitBtn = document.getElementById('submit-btn')

gradeSelect.addEventListener('change', () => {
  if (gradeSelect.value) {
    streamsSelect.style = "display: block;"
    submitBtn.style = "display: block;"
  } else {
    streamsSelect.style = "display: none;"
    submitBtn.style = "display: none;"
  }
})

// Display stream entry inputs.
var streamsInput = document.querySelector('.streams');
document.getElementById('muilt-btn').addEventListener('click', ()=> {
  streamsInput.style = 'display: block';
})
