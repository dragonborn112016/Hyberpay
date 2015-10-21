/**
 * Created by chitra on 13/10/15.
 */
(function () {
    'use strict';

    var controllerId = 'RightCtrl';

    angular.module('app')
        .controller(controllerId, ['$timeout', '$mdSidenav', '$log',RightCtrl]);

    function RightCtrl($timeout, $mdSidenav, $log) {
        var vm = this;

        vm.activate = activate;



        vm.close = function () {
            $mdSidenav('right').close()
                .then(function () {
                    $log.debug("close RIGHT is done");
                });
        };





        activate();

        function activate() {
        }

    }



})();
