import angular from 'angular';
import 'angular-resource';
import 'angular-route';
import 'angular-ui-bootstrap';

import ClauseService from './service';
import InterfaceComponent from './component';

angular.module('Annotator', ['ngRoute', 'ngResource', 'ui.bootstrap'])

  .directive(
    'keyHandler',
    ['$rootScope', $rootScope => (scope, element) => (
      element.bind('keydown', (event) => { $rootScope.$broadcast('bodySendsKeyDown', event); })
    )])

  .factory('Clauses', ['$resource', ClauseService])

  .component('interface', InterfaceComponent)

  .config(['$locationProvider', '$routeProvider', ($locationProvider, $routeProvider) => {
    $locationProvider
      .html5Mode(false)
      .hashPrefix('!');
    $routeProvider
      .when('/:clauseId', { template: '<interface></interface>' });
  }]);
