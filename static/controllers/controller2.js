/**
 * Created by chitra on 13/10/15.
 */
(function () {
    'use strict';

    var controllerId = 'AppCtrl';

    angular.module('app')
        .controller(controllerId, ['$timeout', '$mdSidenav', '$log','$http', AppCtrl]);

    function AppCtrl($timeout, $mdSidenav, $log, $http) {
        var vm = this;

        vm.activate = activate;


        vm.video = {
            id: 'ZSt9tm3RoUU'
        };

        var str="vm.data.senderName";

        vm.firstChar  = str.charAt(0);

        vm.data=[];

        $http.get('https://api.myjson.com/bins/2za98').success(function(data) {
            vm.data = data;
        });


        vm.isOpen = false;

        vm.selectedMode = 'md-fling';

        vm.selectedDirection = 'right';

        vm.toggleLeft = buildToggler('left');
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

        activate();

        function activate() {
        }

    }



})();
