
    const TOKEN = document.getElementById("ui_token").innerText;

    const MESSAGE_TYPES = {
        CONN_BASE: "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/",
        CONN_UI_BASE: "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections_ui/1.0/",
        UI_BASE: "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/ui/1.0/",
        ADMIN_WALLETCONNECTION_BASE: "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/admin_walletconnection/1.0/"
    };

    const UI_MESSAGE = {
        STATE: MESSAGE_TYPES.UI_BASE + "state",
        STATE_REQUEST: MESSAGE_TYPES.UI_BASE + "state_request",
        INITIALIZE: MESSAGE_TYPES.UI_BASE + "initialize",
    };

    const ADMIN_WALLETCONNECTION = {
        CONNECT: MESSAGE_TYPES.ADMIN_WALLETCONNECTION_BASE + 'connect',
        DISCONNECT: MESSAGE_TYPES.ADMIN_WALLETCONNECTION_BASE + 'disconnect',
        USER_ERROR: MESSAGE_TYPES.ADMIN_WALLETCONNECTION_BASE + ''
    };

    const CONN_UI_MESSAGE = {
        SEND_INVITE: MESSAGE_TYPES.CONN_UI_BASE + "send_invite",
        INVITE_SENT: MESSAGE_TYPES.CONN_UI_BASE + "invite_sent",
        INVITE_RECEIVED: MESSAGE_TYPES.CONN_UI_BASE + "invite_received",

        SEND_REQUEST: MESSAGE_TYPES.CONN_UI_BASE + "send_request",
        REQUEST_SENT: MESSAGE_TYPES.CONN_UI_BASE + "request_sent",
        REQUEST_RECEIVED:MESSAGE_TYPES.CONN_UI_BASE + "request_received",

        SEND_RESPONSE: MESSAGE_TYPES.CONN_UI_BASE + "send_response",
        RESPONSE_SENT: MESSAGE_TYPES.CONN_UI_BASE + "response_sent",
        RESPONSE_RECEIVED: MESSAGE_TYPES.CONN_UI_BASE + "response_received",

        SEND_MESSAGE: MESSAGE_TYPES.CONN_UI_BASE + "send_message",
        MESSAGE_SENT: MESSAGE_TYPES.CONN_UI_BASE + "message_sent",
        MESSAGE_RECEIVED: MESSAGE_TYPES.CONN_UI_BASE + "message_received"
    };

    // Message Router {{{
    var msg_router = {
        routes: [],
        route:
            function(msg) {
                if (msg.type in this.routes) {
                    this.routes[msg.type](msg);
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

    // this is shared data among all the vue instances for simplicity.
    var ui_data = {
        agent_name: '',
        passphrase: '',
        current_tab: 'login',
        new_connection_offer: {
            name: "",
            endpoint: ""
        },
        connections: [],
        history_view: []
    };

    var ui_credentials = new Vue({
        el: '#credentials',
        data: ui_data,
        computed: {
            tab_active: function(){
                return this.current_tab == "credentials";
            }
        }
    });

    var ui_relationships = new Vue({
        el: '#relationships',
        data: ui_data,
        computed: {
            tab_active: function(){
                return this.current_tab == "relationships";
            }
        },
        methods: {
            send_invite: function () {
                msg = {
                    type: CONN_UI_MESSAGE.SEND_INVITE,
                    content: {
                        name: this.new_connection_offer.name,
                        endpoint: this.new_connection_offer.endpoint
                    }
                };
                sendMessage(msg);
            },
            invite_sent: function (msg) {
                this.connections.push({
                    name: msg.content.name,
                    status: "Invite Sent",
                    history: []
                });
            },
            invite_received: function (msg) {
                this.connections.push({
                    name: msg.content.name,
                    invitation_msg: msg.content,
                    status: "Invite Received",
                    history: [history_format(msg.content.history)]
                });
            },

            send_request: function (invitation_msg) {
                msg = {
                    type: CONN_UI_MESSAGE.SEND_REQUEST,
                    content: {
                            name: invitation_msg.name,
                            endpoint: invitation_msg.endpoint.url,
                            key: invitation_msg.connection_key,
                    }
                };
                sendMessage(msg);
            },
            request_sent: function (msg) {
                var c = this.get_connection_by_name(msg.content.name);
                c.status = "Request Sent";
            },
            request_received: function (msg) {
                var c = this.get_connection_by_name(msg.content.name);
                c.status = "Request Received";
                c.connecton_request = msg.content;
                c.history.push(history_format(msg.content.history));

            },
            send_response: function (prevMsg) {
                msg = {
                    type: CONN_UI_MESSAGE.SEND_RESPONSE,
                    content: {
                            name: prevMsg.name,
                            // endpoint_key: prevMsg.endpoint_key,
                            // endpoint_uri: prevMsg.endpoint_uri,
                            endpoint_did: prevMsg.endpoint_did
                    }
                };
                sendMessage(msg);
            },
            response_sent: function (msg) {
                var c = this.get_connection_by_name(msg.content.name);
                c.status = "Response sent";
                c.message_capable = true;
                c.history.push(history_format(msg.content));

            },
            response_received: function (msg) {
                var c = this.get_connection_by_name(msg.content.name);
                c.status = "Response received";
                c.response_msg = msg;
                c.their_did = msg.content.their_did;
                c.message_capable = true;
                c.history.push(history_format(msg.content.history));
                //             displayConnection(msg.content.name, [['Send Message', connections.send_message, socket, msg]], 'Response received');

            },
            send_message: function (c) {
                msg = {
                    type: CONN_UI_MESSAGE.SEND_MESSAGE,
                    content: {
                            name: c.name,
                            message: 'Hello, world!',
                            their_did: c.their_did
                    }
                };
                sendMessage(msg);
            },
            message_sent: function (msg) {
                var c = this.get_connection_by_name(msg.content.name);
                c.status = "Message sent";
            },

            message_received: function (msg) {
                var c = this.get_connection_by_name(msg.content.name);
                c.status = "Message received";
                c.their_did = msg.content.their_did;
                c.history.push(history_format(msg.content.history));
            },
            display_history: function(connection){
                this.history_view = connection.history;
                console.log(this.history_view);
                $('#historyModal').modal({});
            },
            get_connection_by_name: function(name){
               return this.connections.find(function(x){return x.name === msg.content.name;});
            }
        }






    });

    // UI Agent {{{
    var ui_agent = new Vue({
        el: '#login',
        data: ui_data,
        computed: {
            tab_active: function(){
                return this.current_tab == "login";
            }
        },
        methods: {
            walletconnnect: function () {
                sendMessage({
                    type: ADMIN_WALLETCONNECTION.CONNECT,
                    name: this.agent_name,
                    passphrase: this.passphrase,
                });
            },
            connect: function(){
                sendMessage(
                    {
                        type: UI_MESSAGE.STATE_REQUEST,
                        content: null
                    }
                );
            },
            update: function (msg) {
                state = msg.content;
                if (state.initialized === false) {
                    this.current_tab = 'login';
                } else {
                    this.agent_name = state.agent_name;
                    this.current_tab = 'relationships';
                }
            }
        }
    });


    // }}}

    // Message Routes {{{
    msg_router.register(UI_MESSAGE.STATE, ui_agent.update);
    msg_router.register(CONN_UI_MESSAGE.INVITE_SENT, ui_relationships.invite_sent);
    msg_router.register(CONN_UI_MESSAGE.INVITE_RECEIVED, ui_relationships.invite_received);
    msg_router.register(CONN_UI_MESSAGE.REQUEST_SENT, ui_relationships.request_sent);
    msg_router.register(CONN_UI_MESSAGE.RESPONSE_SENT, ui_relationships.response_sent);
    msg_router.register(CONN_UI_MESSAGE.MESSAGE_SENT, ui_relationships.message_sent);
    msg_router.register(CONN_UI_MESSAGE.RESPONSE_RECEIVED, ui_relationships.response_received);
    msg_router.register(CONN_UI_MESSAGE.REQUEST_RECEIVED, ui_relationships.request_received);
    msg_router.register(CONN_UI_MESSAGE.MESSAGE_RECEIVED, ui_relationships.message_received);

    // }}}

    // Create WebSocket connection.
    const socket = new WebSocket('ws://' + window.location.hostname + ':' + window.location.port + '/ws');

    // Connection opened
    socket.addEventListener('open', function(event) {
        ui_agent.connect();
    });

    // Listen for messages
    socket.addEventListener('message', function (event) {
        console.log('Routing: ' + event.data);
        msg = JSON.parse(event.data);
        msg_router.route(msg);
    });

    function sendMessage(msg){
        //decorate message as necessary
        msg.ui_token = TOKEN; // deprecated
        msg.id = (new Date()).getTime(); // ms since epoch
        //TODO: Encode properly
        socket.send(JSON.stringify(msg));
    }
