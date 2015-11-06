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



        vm.go = function ( path ) {
            $location.path( path );
        };



        vm.data=[];
        vm.pre_data =[];

        $http.get('http://localhost:8000/accounts/profile/').success(function(data) {
            vm.pre_data =angular.fromJson(data);
            for(var i=0; i<vm.pre_data.length; i++){
            vm.data.push({sender:vm.pre_data[i].sender,date:vm.pre_data[i].date,html_content:$sce.trustAsHtml(vm.pre_data[i].html_content),ammount:vm.pre_data[i].ammount, label:vm.pre_data[i].label})
        }

        });

        vm.data.category = "Recharge";





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
            /* cal */





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
