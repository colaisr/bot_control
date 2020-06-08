$(document).ready(function () {

//  function notifyU(event) {
//      document.getElementById('mbUploading').removeAttribute("hidden");
//  }
//  const formU = document.getElementById('fUpload');
//  formU.addEventListener('submit', notifyU);
//  $('.action-toggle').bootstrapToggle({
//        on: 'Stop',
//        off: 'Start',
//        onstyle: 'danger',
//        offstyle: 'success'
//  });



  $('.action-toggle').change(function() {

    data = {isStart: $(this).prop('checked'), botId: $(this).data('botid')}

    $.get( "/action", data, function(data) {
//<!--        TODO:bootstrap alert response-->
    })
//<!--    .done(function() {-->
//<!--        -->
//<!--    })-->
    .fail(function(error) {
//<!--        TODO: alert error-->
    })
//<!--    .always(function() {-->
//<!--        -->
//<!--    });-->

  });

  $('.modal-opener').click(function () {
  debugger;
        var url = $(this).data('whatever');
        var title = $(this).data('title');
        var button = $(this).data('action-button');
        $.get(url, function (data) {
            $('#botModal .modal-title').html(title);
            $("#submit").html(button);
            $('#botModal .modal-body').html(data);
            $('#botModal').modal();
            $('#submit').click(function (event) {
                event.preventDefault();
                $.post(url, data = $('#botModalForm').serialize(), function (
                    data) {
                    if (data.status == 'ok') {
                        $('#botModal').modal('hide');
                        location.reload();
                    } else {
                        var obj = JSON.parse(data);
                        for (var key in obj) {
                            if (obj.hasOwnProperty(key)) {
                                var value = obj[key];
                            }
                        }
                        $('.help-block').remove()
                        $('<p class="help-block">' + value + '</p>')
                            .insertAfter('#' + key);
                        $('.form-group').addClass('has-error')
                    }
                })
            });
        })
    });

});





