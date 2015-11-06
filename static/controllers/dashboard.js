/**
 * Created by chitra on 5/11/15.
 */
(function () {
    'use strict';

    var controllerId = 'DashCtrl';

    angular.module('app')
        .controller(controllerId, ['$http',DashCtrl]);

    function DashCtrl($http) {
        var vm = this;
        vm.activate = activate;


        var date = new Date();
        var d = date.getDate();
        var m = date.getMonth();
        var y = date.getFullYear();



        var staticEventSource = [] ;

        vm.eventSources = [
            staticEventSource
        ];


        $http.get('https://api.myjson.com/bins/3r71g').success(function(data) {
            var staticEventSources = angular.fromJson(data);

            for(var i=0;i<staticEventSources.length;i++){

                staticEventSource.push({title:staticEventSources[i].title,start:new Date(staticEventSources[i].y,staticEventSources[i].m-1,staticEventSources[i].d)})
            }

            vm.eventSources = [
                staticEventSource
            ];
            console.log(vm.eventSources);

        });

        vm.eventSources = [
            staticEventSource
        ];

        vm.uiConfig = {

            calendar:{

                height: 350,
                editable: true,
                header:{
                    left: 'today ',
                    center: 'title',
                    right: 'prev,next'
                }

            }
        };

        activate();

        function activate() {
        }

    }



})();
