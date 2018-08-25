(function(){

    const TOKEN = document.getElementById("ui_token").innerText;

    const MESSAGE_TYPES = {
        STATE: "urn:sovrin:agent:message_type:sovrin.org/ui/state",
        STATE_REQUEST: "urn:sovrin:agent:message_type:sovrin.org/ui/state_request",
        SEND_OFFER: "urn:sovrin:agent:message_type:sovrin.org/ui/send_offer",
        SEND_OFFER_ACCEPTED: "urn:sovrin:agent:message_type:sovrin.org/ui/send_offer_accepted",
        SENDER_SEND_OFFER_REJECTED: "urn:sovrin:agent:message_type:sovrin.org/ui/sender_send_offer_rejected",
        RECEIVER_SEND_OFFER_REJECTED: "urn:sovrin:agent:message_type:sovrin.org/ui/receiver_send_offer_rejected",
        SENDER_OFFER_REJECTED: "urn:sovrin:agent:message_type:sovrin.org/ui/sender_offer_rejected",
        RECEIVER_OFFER_REJECTED: "urn:sovrin:agent:message_type:sovrin.org/ui/receiver_offer_rejected",
        SEND_CONN_REJECTED: "urn:sovrin:agent:message_type:sovrin.org/ui/send_connection_rejected",
        INITIALIZE: "urn:sovrin:agent:message_type:sovrin.org/ui/initialize",
        OFFER_RECEIVED: "urn:sovrin:agent:message_type:sovrin.org/ui/offer_received",
        OFFER_SENT: "urn:sovrin:agent:message_type:sovrin.org/ui/offer_sent",
        OFFER_ACCEPTED: "urn:sovrin:agent:message_type:sovrin.org/ui/offer_accepted",
        OFFER_ACCEPTED_SENT: "urn:sovrin:agent:message_type:sovrin.org/ui/offer_accepted_sent",
        CONN_REJECTED: "urn:sovrin:agent:message_type:sovrin.org/ui/connection_rejected"
    };

    var connections_wrapper = $('#connections-wrapper');

    // Message Router {{{
    var msg_router = {
        routes: [],
        route:
            function(socket, msg) {
                if (msg.type in this.routes) {
                    this.routes[msg.type](socket, msg);
                } else {
                    console.log('Message from server without registered route: ' + JSON.stringify(msg));
                }
            },
        register:
            function(msg_type, fn) {
                this.routes[msg_type] = fn
            }
    };
    // }}}

    // UI Agent {{{
    var ui_agent = {
        connect:
        function (socket) {
            socket.send(JSON.stringify(
                {
                    type: MESSAGE_TYPES.STATE_REQUEST,
                    id: TOKEN,
                    message: null
                }
            ));
        },
        update:
        function (socket, msg) {
            state = msg.message;
            if (state.initialized == false) {
                showTab('login');
            } else {
                document.getElementById('agent_name').value = state.agent_name;
                document.getElementById('agent_name_header').innerHTML = state.agent_name;
                showTab('relationships');
            }
        },
        inititialize:
        function (socket) {
            init_message = {
                type: MESSAGE_TYPES.INITIALIZE,
                id: TOKEN,
                message: {
                    name: document.getElementById('agent_name').value,
                    passphrase: document.getElementById('passphrase').value
                }
            };
            socket.send(JSON.stringify(init_message));
        },
    };
    // }}}

    function showTab(id) {
        let i;
        let x = document.getElementsByClassName("tab");
        for (i = 0; i < x.length; i++) {
            x[i].style.display = "none";
        }
        document.getElementById(id).style.display = "block";
    }

    // Connections {{{
    var connections = {
        send_offer:
        function (socket) {
            msg = {
                type: MESSAGE_TYPES.SEND_OFFER,
                id: TOKEN,
                message: {
                    name: document.getElementById('send_name').value,
                    endpoint: document.getElementById('send_endpoint').value
                }
            };
            socket.send(JSON.stringify(msg));
        },
        offer_sent:
        function (socket, msg) {
            var context = {name: msg.message.name};
            var contextObj = pending_connection_template(context);
            connections_wrapper.append(contextObj);

            document.getElementById(msg.message.name + '_reject').addEventListener(
                "click",
                function (event) {
                     connections.sender_send_offer_rejected(socket, msg);
                }
            );
        },
        offer_recieved:
        function (socket, msg) {
            var context = {name: msg.message.name};
            var contextObj = received_connection_template(context);
            connections_wrapper.append(contextObj);

            document.getElementById(msg.message.name + '_accept').addEventListener(
                "click",
                function (event) {
                    connections.send_offer_accepted(socket, msg)
                }
            );
            document.getElementById(msg.message.name + '_reject').addEventListener(
                "click",
                function (event) {
                     connections.receiver_send_offer_rejected(socket, msg)
                }
            );
        },
        send_offer_accepted:
        function (socket, msg) {
            accepted_msg = {
                type: MESSAGE_TYPES.SEND_OFFER_ACCEPTED,
                id: TOKEN,
                message: {
                        name: msg.message.name,
                        id: msg.message.id
                }
            };
            socket.send(JSON.stringify(accepted_msg));
        },
        offer_accepted_sent:
        function (socket, msg) {
            var context = {name: msg.message.name};
            var contextObj = connection_template(context);
            removeElementById(msg.message.name + '_received');
            connections_wrapper.append(contextObj);

            document.getElementById(msg.message.name + '_reject').addEventListener(
                "click",
                function (event) {
                     connections.send_conn_rejected(socket, msg)
                }
            );
        },
        offer_accepted:
        function (socket, msg) {
            var context = {name: msg.message.name};
            var contextObj = connection_template(context);
            removeElementById(msg.message.name + '_pending');
            connections_wrapper.append(contextObj);

            document.getElementById(msg.message.name + '_reject').addEventListener(
                "click",
                function (event) {
                     connections.send_conn_rejected(socket, msg)
                }
            );
        },
        receiver_send_offer_rejected:
        function (socket, msg) {
            rejected_msg = {
                type: MESSAGE_TYPES.RECEIVER_SEND_OFFER_REJECTED,
                id: TOKEN,
                message: {
                        name: msg.message.name,
                        id: msg.message.id
                }
            };
            socket.send(JSON.stringify(rejected_msg));
        },
        sender_send_offer_rejected:
        function (socket, msg) {
            rejected_msg = {
                type: MESSAGE_TYPES.SENDER_SEND_OFFER_REJECTED,
                id: TOKEN,
                message: {
                        name: msg.message.name,
                        id: msg.message.id
                }
            };
            socket.send(JSON.stringify(rejected_msg));
        },
        sender_offer_rejected:
        function (socket, msg) {
            removeElementById(msg.message['name'] + '_pending');
        },
        receiver_offer_rejected:
        function (socket, msg) {
            removeElementById(msg.message['name'] + '_received');
        },
        send_conn_rejected:
        function (socket, msg) {
            rejected_msg = {
                type: MESSAGE_TYPES.SEND_CONN_REJECTED,
                id: TOKEN,
                message: {
                        name: msg.message.name,
                        id: msg.message.id
                }
            };
            socket.send(JSON.stringify(rejected_msg));
        },
        conn_rejected:
        function (socket, msg) {
            removeElementById(msg.message.name + '_connection')
        }
    };
    // }}}

    // Templates {{{

    const pending_connection_template = Handlebars.compile(document.getElementById('pending_connection-template').innerHTML);
    const received_connection_template = Handlebars.compile(document.getElementById('received_connection-template').innerHTML);
    const connection_template = Handlebars.compile(document.getElementById('connection-template').innerHTML);

    // }}}

    // Message Routes {{{
    msg_router.register(MESSAGE_TYPES.STATE, ui_agent.update);
    msg_router.register(MESSAGE_TYPES.OFFER_SENT, connections.offer_sent);
    msg_router.register(MESSAGE_TYPES.OFFER_RECEIVED, connections.offer_recieved);
    msg_router.register(MESSAGE_TYPES.OFFER_ACCEPTED, connections.offer_accepted);
    msg_router.register(MESSAGE_TYPES.OFFER_ACCEPTED_SENT, connections.offer_accepted_sent);
    msg_router.register(MESSAGE_TYPES.SENDER_OFFER_REJECTED, connections.sender_offer_rejected);
    msg_router.register(MESSAGE_TYPES.RECEIVER_OFFER_REJECTED, connections.receiver_offer_rejected);
    msg_router.register(MESSAGE_TYPES.CONN_REJECTED, connections.conn_rejected);

    // }}}
    
    // Create WebSocket connection.
    const socket = new WebSocket('ws://' + window.location.hostname + ':' + window.location.port + '/ws');

    // Connection opened
    socket.addEventListener('open', function(event) {
        ui_agent.connect(socket);
    });

    // Listen for messages
    socket.addEventListener('message', function (event) {
        console.log('Routing: ' + event.data);
        msg = JSON.parse(event.data);
        msg_router.route(socket, msg);
    });

    // DOM Event Listeners {{{
    // Need reference to socket so must be after socket creation
    document.getElementById('send_offer').addEventListener(
        "click",
        function (event) { connections.send_offer(socket); }
    );

    document.getElementById('agent_init').addEventListener(
        "click",
        function (event) { ui_agent.inititialize(socket); }
    );

    // }}}

})();
