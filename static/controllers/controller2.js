/**
 * Created by chitra on 13/10/15.
 */
(function () {
    'use strict';

    var controllerId = 'AppCtrl';

    angular.module('app')
        .controller(controllerId, ['$location', AppCtrl]);

    function AppCtrl( $location) {
        var vm = this;

        vm.activate = activate;


        //vm.video = {
        //    id: 'ZSt9tm3RoUU'
        //};


        /*gmail login*/

        vm.go = function ( path ) {
            $location.path( path );
        };










            /* cal */







        activate();

        function activate() {
        }

    }

})();
