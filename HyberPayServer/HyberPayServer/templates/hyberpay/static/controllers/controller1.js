(function () {
    'use strict';

    var controllerId = 'AppCtrl';

    angular.module('app')
        .controller(controllerId, [AppCtrl]);

    function AppCtrl() {
        var vm = this;

        vm.activate = activate;

        vm.imagePath= "images/person.jpg";
        vm.messages = [{
            face : vm.imagePath,

            who: 'Min Li Chan',
            when: '3:08PM'

        }, {
            face : vm.imagePath,

            who: 'Min Li Chan',
            when: '3:08PM'

        },  {
            face : vm.imagePath,
            who: 'Min Li Chan',
            when: '3:08PM'
        }, {
            face : vm.imagePath,
            who: 'Min Li Chan',
            when: '3:08PM'
        }];






        vm.isOpen = false;

        vm.selectedMode = 'md-fling';

        vm.selectedDirection = 'left';

        activate();

        function activate() {
        }

    }



})();
