import angular from 'angular';
import 'angular-resource';
import 'angular-route';
import 'angular-ui-bootstrap';

import ClauseService from './service';
import InterfaceController from './controller';

angular.module('Annotator', ['ngRoute', 'ngResource', 'ui.bootstrap'])

  .factory('Clauses', ClauseService)

  .config(($locationProvider, $routeProvider) => {
    $locationProvider
      .html5Mode(false)
      .hashPrefix('!');
    $routeProvider
      .when('/:clauseId', InterfaceController);
  });
