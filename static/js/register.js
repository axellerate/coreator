//validation

$(document).ready(function(){
  function validateEmail(email) {
      var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
      return re.test(email);
  }

  function checkIfUserExists(email, valid){
    var result = $.get("http://localhost:15080/_ah/api/users/1.00/check_user_exists?email="+email, function(data){
      if(data['success']){
        $("#email").css("border", "2px solid red");
        $("#email_error").html(" That email already exists.");
        $("#email_error").show();
        $("#email_valid").hide();
        return true;
      }
      return false;
    });
  }

  var valid = true;
  $("#email").focusout(function(){
    var check = validateEmail($("#email").val());
    if (check){
      valid = true;
      $("#email_error").hide();
      $("#email_valid").show();
      $("#email").css("border", "2px solid green");
      checkIfUserExists($("#email").val(), valid);
    }else{
      valid = false;
      $("#email_error").show();
      $("#email_error").html(" Invalid email address");
      $("#email_valid").hide();
      $("#email").css("border", "2px solid red");
    }

  });
  $("#password").focusout(function(){
    var length = $("#password").val().length;
    if (length > 5){
      valid = true;
      $("#password_error").hide();
      $("#password_valid").show();
      $("#password").css("border", "2px solid green");
    }else{
      valid = false;
      $("#password_error").show();
      $("#password_valid").hide();
      $("#password").css("border", "2px solid red");
    }
    var password = $("#password").val();
    var retype_password = $("#retype_password").val();
    if(retype_password.length != 0){
      if (password === retype_password){
        valid = true;
        $("#retype_password_error").hide();
        $("#retype_password_valid").show();
        $("#retype_password").css("border", "2px solid green");
      }else{
        valid = false;
        $("#retype_password_error").show();
        $("#retype_password_valid").hide();
        $("#retype_password").css("border", "2px solid red");
      }
    }
  });
  $("#retype_password").focusout(function(){
    var password = $("#password").val();
    var retype_password = $("#retype_password").val();
    if (password === retype_password){
      valid = true;
      $("#retype_password_error").hide();
      $("#retype_password_valid").show();
      $("#retype_password").css("border", "2px solid green");
    }else{
      valid = false;
      $("#retype_password_error").show();
      $("#retype_password_valid").hide();
      $("#retype_password").css("border", "2px solid red");
    }
  });
  $("#first_name").focusout(function(){
    var first_name = $("#first_name").val().length;
    if (first_name > 0){
      valid = true;
      $("#first_name_error").hide();
      $("#first_name_valid").show();
      $("#first_name").css("border", "2px solid green");
    }else{
      valid = false;
      $("#first_name_error").show();
      $("#first_name_valid").hide();
      $("#first_name").css("border", "2px solid red");
    }
  });
  $("#last_name").focusout(function(){
    var last_name = $("#last_name").val().length;
    if (last_name > 0){
      valid = true;
      $("#last_name_error").hide();
      $("#last_name_valid").show();
      $("#last_name").css("border", "2px solid green");
    }else{
      valid = false;
      $("#last_name_error").show();
      $("#last_name_valid").hide();
      $("#last_name").css("border", "2px solid red");
    }
  });


  //register a user
  if(valid == true){
    $('#register_button').click(function() {
      var $email = $("#email").val();
      var $password = $("#password").val();
      var $retype_password = $("#retype_password").val();
      var $first_name = $("#first_name").val();
      var $last_name = $("#last_name").val();
      var $profession = $("#profession").val();

      var $flag = true;

      var check = validateEmail($("#email").val());
      if (check){
        valid = true;
        $("#email_error").hide();
        $("#email_valid").show();
        $("#email").css("border", "2px solid green");
        checkIfUserExists($("#email").val(), valid);
      }

      if($email == ""){
        $("#email_error").show();
        $("#email_error").html(" Invalid email address");
        $("#email_valid").hide();
        $("#email").css("border", "2px solid red");
        $flag = false;
      }else{
        if(checkIfUserExists($("#email").val(), valid)){
          $flag = false;
        }

        if( !validateEmail($("#email").val()) ){
          $flag = false;
        }
      }

      if($password == ""){
        $("#password_error").show();
        $("#password_valid").hide();
        $("#password").css("border", "2px solid red");
        $flag = false;
      }

      if($password != $retype_password){
        $("#retype_password_error").show();
        $("#retype_password_valid").hide();
        $("#retype_password").css("border", "2px solid red");
        $flag = false;
      }else{
        $("#retype_password_error").hide();
        $("#retype_password_valid").show();
        $("#retype_password").css("border", "2px solid green");
      }

      if($retype_password  == ""){
        $("#retype_password_error").show();
        $("#retype_password_valid").hide();
        $("#retype_password").css("border", "2px solid red");
        $flag = false;
      }


      if($first_name == ""){
        $("#first_name_error").show();
        $("#first_name_valid").hide();
        $("#first_name").css("border", "2px solid red");
        $flag = false;
      }

      if($last_name == ""){
        $("#last_name_error").show();
        $("#last_name_valid").hide();
        $("#last_name").css("border", "2px solid red");
        $flag = false;
      }

      if($profession == ""){
        $flag = false;
      }

      if($flag == false){
        return;
      }

      var $data = { "email": $email, "password": $password,
                    "first_name": $first_name, "last_name": $last_name,
                    "profession": $profession};

      $.ajax({
        type: "POST",
        url: 'http://localhost:15080/_ah/api/users/1.00/create',
        data: JSON.stringify($data),
        contentType: "application/json",
        success:function(data)
        {
          setCookie("coreator_auth_token",data['token'], 30);
          $("#user_email").html(data['email']);
          $("#user_first_name").html(data['first_name']);
          $("#user_last_name").html(" "+data['last_name']+" ");

          window.location.replace("/");
        },
        beforeSend:function(){

        },
        error:function(data){

        }
      });
    });
  }


  //populate professions
  $.get("http://localhost:15080/_ah/api/professions/v1/get_professions", function(data, status){
    $.each(data['professions'], function (index, value) {
        $('#profession').append($('<option/>', { 
            value: value['slug'],
            text : value['name']
        }));
    });   
  });


});