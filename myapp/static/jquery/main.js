$(document).ready(function(){
    $('#login_btn').click(function(){
        var username = $('#username').val();
        var password = $('#password').val();
        if (username == '' || password == '' ) {
            $('#error').text('Please complete all filleds')
            $('#error').css('color','red')
            $('#username').css('border','1px solid red')
            $('#password').css('border','1px solid red')
            //alert('Please fill all filled')
            event.preventDefault();
        }

        else{
            $('#error').text('')
            $('#username').css('border','1px solid lightgray')
            $('#password').css('border','1px solid lightgray')
           // alert('Successful')
        }
        //validateForm();
    })

    $('#basic-addon1').click(function(){
        var showPassword = document.getElementById("password");
        if (showPassword.type === "password") {
            showPassword.type = "text";
            } else {
                showPassword.type = "password";
        }
    })


    $('#checkbox').click(function(){
    var agreement = $('#checkbox').prop('checked')
    if (agreement == true) {
        $('#login_btn').prop('disabled', false)
    }
    else{
        $('#login_btn').prop('disabled', true)
    }
})

$('input').click(function(){
    $(this).css('border','1px solid lightgray')
})


})