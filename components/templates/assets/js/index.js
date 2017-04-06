var domain_variable = "localhost";
var web_socket_url = "ws://"+ domain_variable +":8000/client_push_server/";

$(document).ready(function(){
    var websocket_instance = new WebSocket(web_socket_url);
    console.log("socket connection with server successfull!");
    var number_input_id = "number-input";
    var number_input_button_id = "number-input-button";

    $("#"+ number_input_button_id).click(function(){
        try{
            var ajax_data = {};
            ajax_data["number"] = $("#number-input").val();
            console.log(ajax_data);

        }
        catch(err){
            alert(err.message);
        }
    });

    websocket_instance.onmessage = function(event){
        console.log(event.data);
        var data_obj = JSON.parse(event.data);
        
        if("error" in data_obj){
                alert(data_obj["error"]);
            }
            else if("success" in data_obj){
                console.log(data_obj["success"]);
            }
            else if("number_input_hook" in data_obj){
                $("#landing-page-container").css("display","none");
                $("#otp-page-container").css("display","block");

                $("#number-input-button").click(function(){

                    var ajax_data = {"number":"+91" + $("#number-input").val()};
                    console.log(ajax_data);
                    var sms_api_url = "http://" + domain_variable + ":8000/send_sms/";
                    $.ajax({
                        type:'POST',
                        url: sms_api_url,
                        data: JSON.stringify(ajax_data),
                        dataType: 'text'
                    }).done(function(){
                        $("#user-area").empty();
                        var otp_input_element = document.createElement("input");
                        var otp_submit_element = document.createElement("input");

                        $(otp_input_element).attr("id", "otp-input");
                        $(otp_input_element).attr("name", "otp");
                        $(otp_input_element).attr("type","text");

                        $(otp_input_element).attr("placeholder", "input your otp");
                        $(otp_submit_element).attr("id", "otp-input-submit");
                        $(otp_submit_element).attr("type", "submit");
                        $(otp_submit_element).text("submit");


                        var otp_form_element = document.createElement("form");

                        $(otp_form_element).attr("id", "otp-form");
                        $(otp_form_element).attr("method", "post");
                        $(otp_form_element).attr("action", "/allow_internet/");

                        $(otp_form_element).append(otp_input_element);
                        $(otp_form_element).append(otp_submit_element);

                        $("#user-area").append(otp_form_element);
                    }).error(function(){
                        console.log("testing error");
                    });
                });
            }
            else{
                $(new_message_div).text("OOPS.. Something went wrong!!");
            }
        $("#user-area").append(new_message_div);
    };

});