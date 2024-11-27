// basic search input customization.
let radioBtns = document.getElementsByClassName('form-check-input');
let searchInput = document.getElementsByClassName('custom-form-control')[0];

for (let i = 0; i < radioBtns.length; i++) {
  radioBtns[i].addEventListener('change', function() {
    if (radioBtns[i].checked) { 
      if (radioBtns[i].value == 'Enter adm no') {
        searchInput.setAttribute('placeholder', 'Enter adm no');
        searchInput.setAttribute('type', 'number');
      } else if (radioBtns[i].value == 'Enter name') {
        searchInput.setAttribute('placeholder', 'Enter name');
        searchInput.setAttribute('type', 'text');
      } else {
        searchInput.setAttribute('placeholder', 'Enter UPI no');
        searchInput.setAttribute('type', 'text');
      }
    }
  });
}