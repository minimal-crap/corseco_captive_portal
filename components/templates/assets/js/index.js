var domain_variable = "192.168.42.1";
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

//    $('#' + number_input_id).click(function(){
//        try{
//            var ajax_data = {};
//            var ajax_data["number"] = $('#'+number_input_id).val();
//            var sms_api_url = "http://" + domain_variable + ":8000/send_sms/";
//            $.ajax({
//                type:'POST',
//		        url: sms_api_url,
//		        data:JSON.stringify(ajax_data),
//		        dataType:'text'
//                }).done(function(){
//                    $("#user-area").empty();
//                    //form creation logic goes here
//                    console.log("message sent successfully!");
//                });
//        }
//        catch(err){
//            alert("number-input-button::click: " + err.message);
//        }
//    });

    websocket_instance.onmessage = function(event){
        console.log(event.data);
        var data_obj = JSON.parse(event.data);
        $("#user-area").empty();
        var new_message_div = document.createElement("div");
        if("error" in data_obj){
                $(new_message_div).text(data_obj["error"]);
            }
            else if("success" in data_obj){
                $(new_message_div).text(data_obj["success"]);
            }
            else if("number_input_hook" in data_obj){

                var input_element = document.createElement("input");
                var submit_button_element = document.createElement("button");
                $(input_element).attr("id", number_input_id);
                $(input_element).attr("placeholder", "input your number");
                $(submit_button_element).attr("id", number_input_button_id);
                $(submit_button_element).text("submit");
                $("#user-area").append(input_element);
                $("#user-area").append(submit_button_element);
                $("#"+ number_input_button_id).click(function(){
                    var ajax_data = {"number":$("#number-input").val()};
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
                    });
                });
            }
            else{
                $(new_message_div).text("OOPS.. Something went wrong!!");
            }
        $("#user-area").append(new_message_div);
    };

});