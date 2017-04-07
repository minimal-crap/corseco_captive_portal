var domain = "192.168.42.1";
var port = 8000;
var web_socket_url = "ws://" + domain + ":" + port.toString() + "/client_push_server/";
var sms_api_url = "http://" + domain + ":" + port.toString() +"/send_sms/";
var sms_api_ajax_param = {
    type:"POST",
    url: sms_api_url,
    data: "",
    dataType: "text"
}
$(document).ready(function(){
    try{
        //create web socket connection to the push server
        var websocket_instance = new WebSocket(web_socket_url);
        console.log("[*]web socket connetcted!");

        // web socket event when message is received 
        // at client side pushed from the server
        websocket_instance.onmessage =function(event){
            try{
                console.log(event.data);
                var parsed_server_message = JSON.parse(event.data);

                // when a client is in queue
                if("error" in parsed_server_message){

                    // hide portal landing page and show error
                    $('#landing-page-container').css("display", "none");
                    $('#error-div').text(parsed_server_message["error"]);
                    $('#error-message-container').css("display", "block");
                    
                }

                // when no other client in queue
                else if("success" in parsed_server_message){
                    console.log(event.data);
                    // hide error and show portal landing page
                }
                // when barcode is scanned at counter
                else if("number_input_hook" in parsed_server_message){
                    // hide landing portal page and show
                    // number input control
                    $("#landing-page-container").css("display","none");
                    $("#otp-page-container").css("display","block");

                    // number input click event handler
                    $("#number-input-button").click(function(){
                        var sms_api_post_data = {
                            "number": "+91" + $("#number-input").val()
                        };
                        sms_api_ajax_param["data"] = JSON.stringify(sms_api_post_data);
                        // make ajax call to sms api
                        $.ajax(sms_api_ajax_param).done(function(){
                            $("#input-area").empty();

                            // create form child elements
                            var otp_input_element = document.createElement("input");
                            var otp_submit_element = document.createElement("input");

                            $(otp_input_element).attr("id", "otp-input");
                            $(otp_input_element).attr("name", "otp");
                            $(otp_input_element).attr("type","text");

                            $(otp_input_element).attr("placeholder", "input your otp");
                            $(otp_submit_element).attr("id", "otp-input-submit");
                            $(otp_submit_element).attr("type", "submit");
                            $(otp_submit_element).text("submit");

                            // create form element
                            var otp_form_element = document.createElement("form");

                            $(otp_form_element).attr("id", "otp-form");
                            $(otp_form_element).attr("method", "post");
                            $(otp_form_element).attr("action", "/allow_internet/");

                            $(otp_form_element).append(otp_input_element);
                            $(otp_form_element).append(otp_submit_element);

                            // create otp input message division
                            var otp_label_element = document.createElement("div");
                            $(otp_label_element).css({
                                "color": "#ffe700",
                                "font-size": "28",
                                "font-weight": "bolder",
                                "text-align": "center"
                            });
                            $(otp_label_element).text("ENTER THE OTP");

                            $("#input-area").append(otp_label_element);
                            $("#input-area").append(otp_form_element);
                        });
                    });
                }
                else{
                    alert("websocket_instance::onmessage: unexpected response from push server - " + event.data);
                }
            }
            catch(err){
                alert("websocket_instance::onmessage :" + err.message);
            }
        };
    }
    catch(err){
        alert("document::ready: " + err.message);
    }
});
