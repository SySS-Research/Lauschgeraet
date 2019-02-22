$(document).ready(function() {
  $('.ajax-switch').change(toggle_onoff);
});

function toggle_onoff() {
  $.ajax({
    url: '/toggleswitch',
    data: {"name":this.id},
    type: 'POST',
  });
}

$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
});

function ruleAbort() {
        $('#iptables-table > tbody > tr:last-child').remove();
}
function ruleAdd() {
    var proto = $('#new-rule-proto').val();
    var port = $('#new-rule-port').val();
    var olddest = $('#new-rule-olddest').val();
    var newdest = $('#new-rule-newdest').val();
    $.ajax({
        url: '/addrule',
        data: {
            "proto": proto,
            "port": port,
            "olddest": olddest,
            "newdest": newdest,
        },
        type: 'POST',
    });
    location.reload();
}

$(document).ready(function(){
	$('#add-iptables-rule').click(function(){
        $('#iptables-table > tbody:last-child').append(`<tr>
                <td></td>
                <td><input id="new-rule-proto"></input></td>
                <td><input id="new-rule-port"></input></td>
                <td><input id="new-rule-olddest"></input></td>
                <td><input id="new-rule-newdest"></input></td>
                <td>
                  <a href='#' class="nav-item" onClick='ruleAdd()'><span data-feather="plus-circle"></span></a>
                  <a href='#' class="nav-item" onClick='ruleAbort()'><span data-feather="x"></span></a>
                </td>
            </tr>`);

        feather.replace();
    });
});
