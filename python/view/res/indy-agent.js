(function(){

    const TOKEN = document.getElementById("ui_token").innerText;

    var conns = {};
    var pending_conns = {};
    var received_conns = {};

    connectionsTable = document.getElementById("conns-new");

    const MESSAGE_TYPES = {
        STATE: "urn:sovrin:agent:message_type:sovrin.org/ui/state",
        STATE_REQUEST: "urn:sovrin:agent:message_type:sovrin.org/ui/state_request",
        INITIALIZE: "urn:sovrin:agent:message_type:sovrin.org/ui/initialize",

        UI: {
            SEND_INVITE: "urn:sovrin:agent:message_type:sovrin.org/ui/send_invite",
            INVITE_SENT: "urn:sovrin:agent:message_type:sovrin.org/ui/invite_sent",
            INVITE_RECEIVED: "urn:sovrin:agent:message_type:sovrin.org/ui/invite_received",

            SEND_REQUEST: "urn:sovrin:agent:message_type:sovrin.org/ui/send_request",
            REQUEST_SENT: "urn:sovrin:agent:message_type:sovrin.org/ui/request_sent",
            REQUEST_RECEIVED: "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/request",

            SEND_RESPONSE: "urn:sovrin:agent:message_type:sovrin.org/ui/send_response",
            RESPONSE_SENT: "urn:sovrin:agent:message_type:sovrin.org/ui/response_sent",
            RESPONSE_RECEIVED: "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/response"
        }
    };

    // var message_display = $('#message_display');

    var msg_counter = 0;

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
            if (state.initialized === false) {
                showTab('login');
            } else {
                document.getElementById('agent_name').value = state.agent_name;
                document.getElementById('agent_name_header').innerHTML = "Agent's name: " + state.agent_name;
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

            pending_conns[msg.message.id] = [];
            pending_conns[msg.message.id].push(getTodayDate() + " " + MESSAGE_TYPES.SEND_OFFER + '\n');

            pending_conns[msg.message.id].push(getTodayDate() + " " + MESSAGE_TYPES.OFFER_SENT + '\n');

            displayConnection(msg.message.name, msg.message.id, [['Reject', connections.sender_send_offer_rejected, socket, msg]], 'Pending');
        },
        offer_recieved:
        function (socket, msg) {
            received_conns[msg.message.id] = [];
            received_conns[msg.message.id].push(getTodayDate() + " " + MESSAGE_TYPES.OFFER_RECEIVED + '\n');

            displayConnection(msg.message.name, msg.message.id, [['Reject', connections.receiver_send_offer_rejected, socket, msg],
                                                 ['Accept', connections.send_offer_accepted, socket, msg]], 'Received');
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
            received_conns[msg.message.id].push(getTodayDate() + " " + MESSAGE_TYPES.SEND_OFFER_ACCEPTED + '\n');

            socket.send(JSON.stringify(accepted_msg));
        },
        offer_accepted_sent:
        function (socket, msg) {
            removeElementById(msg.message.name + '_row');

            conns[msg.message.id] = [JSON.parse(JSON.stringify(received_conns[msg.message.id]))];
            delete received_conns[msg.message.id];
            conns[msg.message.id].push(getTodayDate() + " " + MESSAGE_TYPES.OFFER_ACCEPTED_SENT + '\n');

            displayConnection(msg.message.name, msg.message.id, [['Reject', connections.send_conn_rejected, socket, msg]], 'Connected');
        },
        offer_accepted:
        function (socket, msg) {
            removeElementById(msg.message.name + '_row');

            conns[msg.message.id] = [JSON.parse(JSON.stringify(pending_conns[msg.message.id]))];
            delete pending_conns[msg.message.id];
            conns[msg.message.id].push(getTodayDate() + " " + MESSAGE_TYPES.OFFER_ACCEPTED + '\n');

            displayConnection(msg.message.name, msg.message.id, [['Reject', connections.send_conn_rejected, socket, msg]], 'Connected');
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
            received_conns[msg.message.id].push(getTodayDate() + " " + MESSAGE_TYPES.RECEIVER_SEND_OFFER_REJECTED + '\n');

            delete received_conns[msg.message.id];
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
            pending_conns[msg.message.id].push(getTodayDate() + " " + MESSAGE_TYPES.SENDER_SEND_OFFER_REJECTED + '\n');

            delete pending_conns[msg.message.id];

        },
        sender_offer_rejected:
        function (socket, msg) {
            removeElementById(msg.message['name'] + '_row');
        },
        receiver_offer_rejected:
        function (socket, msg) {
            removeElementById(msg.message['name'] + '_row');
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
            conns[msg.message.id].push(getTodayDate() + " " + MESSAGE_TYPES.SEND_CONN_REJECTED + '\n');

            delete conns[msg.message.id];
        },
        conn_rejected:
        function (socket, msg) {
            removeElementById(msg.message.name + '_row');
        }
    };
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
        // msg_counter += 1;

        console.log('Routing: ' + event.data);
        msg = JSON.parse(event.data);
        // message_display.append(msg_counter, " ", JSON.stringify(msg, null, 4), "</br>");
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

    function displayConnection(connName, connId, actions, status) {
        let row = connectionsTable.insertRow();
        row.id = connName + "_row";
        let cell1 = row.insertCell();
        let cell2 = row.insertCell();
        let cell3 = row.insertCell();
        let cell4 = row.insertCell();
        let cell5 = row.insertCell();

        let history_btn = document.createElement("button");
        history_btn.id = connName + "_history";
        history_btn.type = "button";
        history_btn.className = "btn btn-info";
        history_btn.textContent = "View";
        history_btn.setAttribute('data-toggle', 'modal');
        history_btn.setAttribute('data-target', '#exampleModal');

        history_btn.addEventListener(
            "click",
            function (event) {
                if(status === "Connected") {
                    document.getElementById("history_body").innerText = conns[connId].join('');
                }
                else if(status === "Pending") {
                    document.getElementById("history_body").innerText = pending_conns[connId].join('');
                }
                else if(status === "Received") {
                    document.getElementById("history_body").innerText = received_conns[connId].join('');
                }

            }
        );

        actions.forEach(function (item, i, actions) {
            let butn = document.createElement("button");
            butn.id = connName + "_" + item[0];
            butn.type = "button";
            butn.className = "btn btn-warning   ";
            butn.textContent = item[0];
            butn.addEventListener(
                "click",
                function (event) {
                     item[1](item[2], item[3]);
                }
            );
            cell5.appendChild(butn);

        });

        cell1.innerHTML = "#";
        cell2.innerHTML = connName;
        cell3.innerHTML = status;
        cell4.appendChild(history_btn);
    }

    // }}}

})();
