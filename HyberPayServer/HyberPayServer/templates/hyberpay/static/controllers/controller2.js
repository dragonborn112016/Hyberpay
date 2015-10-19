/**
 * Created by chitra on 13/10/15.
 */
(function () {
	
    'use strict';

    var controllerId = 'AppCtrl';

    angular.module('app')
        .controller(controllerId, ['$timeout', '$mdSidenav', '$log',AppCtrl]);

    function AppCtrl($timeout, $mdSidenav, $log) {
        var vm = this;

        vm.activate = activate;

        vm.imagePath= "/static/images/voda.jpg";
        vm.messages = [{
            face : vm.imagePath,
            who: 'FreeCharge'

        }, {
            face : vm.imagePath,
            who: 'BookmyShow'

        },  {
            face : vm.imagePath,
            who: 'MakemyTrip'
        },{
            face : vm.imagePath,
            who: 'IRCTC'
        }, {
            face : vm.imagePath,
            who: 'OYO'
        }];






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
