/**
 * Created by chitra on 12/10/15.
 */
(function () {
    'use strict';

    var app = angular.module('app');

    // Collect the routes
    app.constant('routes', getRoutes());

    // Configure the routes and route resolvers
    app.config(['$routeProvider', '$locationProvider', 'routes', routeConfigurator]);
    function routeConfigurator($routeProvider, $locationProvider, routes) {

        routes.forEach(function (r) {
            $routeProvider.when(r.url, r.config);
            $locationProvider.hashPrefix('!').html5Mode(false);

        });
        console.log("this is from route.config");
        $routeProvider.otherwise({ redirectTo: '/' });
    }

    // Define the routes
    function getRoutes() {
        return [
            {
                url: '/',
                config: {
                    title: 'landingPage',
                    templateUrl: 'portals/loginPage.html',
                    settings: {
                        nav: 2

                    }
                }
            },

            {
                url: '/home',
                config: {
                    title: 'home',
                    templateUrl: 'portals/home.html',
                    settings: {
                        nav: 2

                    }
                }
            }

        ];
    }
})();
