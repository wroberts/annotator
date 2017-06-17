import angular from 'angular';
import 'angular-resource';
import 'angular-route';

import ClauseService from './service';
import template from './interface.html';

const SPAN_TITLES = {
  verb: 'Main verb of the clause',
  subj: 'Subject',
  obj: 'Direct object',
  advp_for: 'Aspectual (for)',
};

angular.module('Annotator', ['ngRoute', 'ngResource'])

  .factory('Clauses', ClauseService)

  .config(($locationProvider, $routeProvider) => {
    $locationProvider
      .html5Mode(false)
      .hashPrefix('!');
    $routeProvider
      .when('/:clauseId', {
        restrict: 'E',
        controller: ($scope, $routeParams, Clauses) => {
          // make the call to the REST API to fetch the clause object
          $scope.spans = [];
          Clauses.get({ id: $routeParams.clauseId },
                      (clause) => {
                        const spanMap = clause.sentence.map(() => undefined);
                        const spanMap2 = clause.sentence.map(() => undefined);
                        for (const comp of clause['aspectual-indicators']) {
                          for (let i = comp.begin; i < comp.end; i += 1)
                            spanMap[i] = comp.type;
                            spanMap2[i] = 'aspind';
                        }
                        for (const comp of clause['verb-comps']) {
                          for (let i = comp.begin; i < comp.end; i += 1) {
                            spanMap[i] = comp.type;
                            spanMap2[i] = 'synarg';
                          }
                        }
                        spanMap[clause['verb-index']] = 'verb';
                        spanMap2[clause['verb-index']] = undefined;
                        $scope.spanMap = spanMap;
                        $scope.spanMap2 = spanMap2;
                        const spans = [];
                        let lastClass;
                        let currentSpan = { wclass: undefined, mclass: undefined, words: [] };
                        for (let i = 0; i < clause.sentence.length - 1; i += 1)
                        {
                          const word = clause.sentence[i];
                          const wclass = spanMap[i];
                          if (wclass === lastClass) {
                            currentSpan.words.push(word);
                          } else {
                            lastClass = wclass;
                            if (currentSpan.words) {
                              currentSpan.idx = spans.length;
                              currentSpan.title = SPAN_TITLES[currentSpan.wclass];
                              if (currentSpan.title) currentSpan.cclass = 'help';
                              currentSpan.words = currentSpan.words.join(' ');
                              spans.push(currentSpan);
                            }
                            currentSpan = { wclass, mclass: spanMap2[i], words: [word] };
                          }
                        }
                        if (currentSpan.words) {
                          currentSpan.idx = spans.length;
                          currentSpan.title = SPAN_TITLES[currentSpan.wclass];
                          if (currentSpan.title) currentSpan.cclass = 'help';
                          currentSpan.words = currentSpan.words.join(' ');
                          spans.push(currentSpan);
                        }
                        $scope.spans = spans;
                      });
          // we use the Clause service's cache to access the clause
          // object in the page
          $scope.cached = Clauses.cache;
          $scope.isClean = Clauses.isClean;
          $scope.save = Clauses.save;
        },
        template,
      });
  });
