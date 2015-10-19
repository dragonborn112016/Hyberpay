/**
 * Created by chitra on 13/10/15.
 */
(function () {
    'use strict';

    var controllerId = 'LeftCtrl';

    angular.module('app')
        .controller(controllerId, ['$timeout', '$mdSidenav', '$log',LeftCtrl]);

    function LeftCtrl ($timeout, $mdSidenav, $log) {
        var vm = this;

        vm.activate = activate;

        vm.close = function () {
            $mdSidenav('left').close()
                .then(function () {
                    $log.debug("close LEFT is done");
                });
        };








        activate();

        function activate() {
        }

    }



})();
