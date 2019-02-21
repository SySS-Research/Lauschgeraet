$(document).ready(function() {
  $('.ajax-switch').change(toggle_onoff);
});

function toggle_onoff() {
    console.log(this.id);
  $.ajax({
    url: '/toggleswitch',
    data: {"name":this.id},
    type: 'POST',
  });
}
