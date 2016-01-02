function setCookie(c_name,value,exdays){
  var exdate=new Date();
  exdate.setDate(exdate.getDate() + exdays);
  var c_value=escape(value) + 
    ((exdays==null) ? "" : ("; expires="+exdate.toUTCString()));
  document.cookie=c_name + "=" + c_value;
}


function getCookie(c_name){
  var i,x,y,ARRcookies=document.cookie.split(";");
  for (i=0;i<ARRcookies.length;i++){
     x=ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
     y=ARRcookies[i].substr(ARRcookies[i].indexOf("=")+1);
     x=x.replace(/^\s+|\s+$/g,"");
     
     if (x==c_name)
     {
      return unescape(y);
     }
  }
}

var delete_cookie = function(name) {
    document.cookie = name + '=;expires=Thu, 01 Jan 1970 00:00:01 GMT;';
};


$("#projects_button").click(function(){
  window.location.href = '/projects';
});

$("#people_button").click(function(){
  window.location.href = '/people';
});

$(document).ready(function(){

var url = window.location.href;
if(url.indexOf("/register") > -1){
  if(getCookie("coreator_auth_token")){
    window.location.replace("/");
  }
}

//check if a user is logged in
if(getCookie("coreator_auth_token")){

  $.get("http://localhost:15080/_ah/api/users/1.00/get_user?token="+getCookie("coreator_auth_token"), function(data, status){
      if(data['email'] != ""){
        $("#login_form").hide();
        $("#user_info_header").show();
        $("#user_projects_header").show();
        $("#user_email").html(data['email']);
        $("#user_first_name").html("<div id='profile_image_header'></div>" + data['first_name']);
        $("#user_last_name").html(" "+data['last_name']+" ");
        $("#create_project_button").show();
      }else{
        $("#login_form").show();
      }
  });

}else{
  $("#login_form").show();
  delete_cookie('coreator_auth_token');
}

});
