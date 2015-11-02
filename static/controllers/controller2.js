/**
 * Created by chitra on 13/10/15.
 */
(function () {
    'use strict';

    var controllerId = 'AppCtrl';

    angular.module('app')
        .controller(controllerId, ['$timeout', '$mdSidenav', '$log','$http','$location','$sce', AppCtrl]);

    function AppCtrl($timeout, $mdSidenav, $log, $http, $location, $sce) {
        var vm = this;

        vm.activate = activate;


        vm.video = {
            id: 'ZSt9tm3RoUU'
        };


        /*gmail login*/


            vm.onSignIn = function(googleUser) {
            console.log("gmail");
            console.log('Logged in as: ' + googleUser.getBasicProfile().getName());

            // Useful data for your client-side scripts:
            var profile = googleUser.getBasicProfile();
            console.log("ID: " + profile.getId()); // Don't send this directly to your server!
            console.log("Name: " + profile.getName());
            console.log("Image URL: " + profile.getImageUrl());
            console.log("Email: " + profile.getEmail());

            // The ID token you need to pass to your backend:
            var id_token = googleUser.getAuthResponse().id_token;
            console.log("ID Token: " + id_token);

        };


        vm.go = function ( path ) {
            $location.path( path );
        };



        vm.data=[];
        vm.pre_data =[];

        $http.get('http://localhost:8000/accounts/profile/').success(function(data) {
            vm.pre_data =angular.fromJson(data);
            
            console.log(vm.pre_data.label);
            for(var i=0; i<vm.pre_data.length; i++){
            vm.data.push({sender:vm.pre_data[i].sender,date:vm.pre_data[i].date,html_content:$sce.trustAsHtml(vm.pre_data[i].html_content),ammount:vm.pre_data[i].ammount,label:vm.pre_data[i].label})
        }

        });







       /* dashboard */

        vm.toggleRight = buildToggler('right');

        function debounce(func, wait, context) {
            var timer;
            return function debounced() {
                var context = vm,
                    args = Array.prototype.slice.call(arguments);
                $timeout.cancel(timer);
                timer = $timeout(function() {
                    timer = undefined;
                    func.apply(context, args);
                }, wait || 10);
            };
        }
        function buildToggler(navID) {
            return debounce(function() {
                $mdSidenav(navID).
                    toggle().
                    then(function () {
                        $log.debug("toggle " + navID + " is done");
                    });
            }, 200);
        }


        /*view */

        vm.show=[];

        for(var i=0;i<vm.data.length;i++){
            vm.show[i] = true;
        }
        var id1;

        vm.clicked = function(id)
        {
            vm.show[id]=!vm.show[id];
            id1 = id;
        };


        activate();

        function activate() {
        }

    }

})();
