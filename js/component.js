import template from './interface.html';

const SPAN_TITLES = {
  verb: 'Main verb of the clause',
  subj: 'Subject',
  obj: 'Direct object',
  advp_for: 'Aspectual (for)',
};

function getSpanMaps(clause) {
  const spanMap = clause.sentence.map(() => undefined);
  const spanMap2 = clause.sentence.map(() => undefined);
  for (const comp of clause['aspectual-indicators']) {
    for (let i = comp.begin; i < comp.end; i += 1) {
      spanMap[i] = comp.type;
      spanMap2[i] = 'aspind';
    }
  }
  for (const comp of clause['verb-comps']) {
    for (let i = comp.begin; i < comp.end; i += 1) {
      spanMap[i] = comp.type;
      spanMap2[i] = 'synarg';
    }
  }
  spanMap[clause['verb-index']] = 'verb';
  spanMap2[clause['verb-index']] = undefined;
  return { spanMap, spanMap2 };
}

function getSpans(clause) {
  const spanMaps = getSpanMaps(clause);
  const spans = [];
  let lastClass;
  let currentSpan = { wclass: undefined, mclass: undefined, words: [] };
  for (let i = 0; i < clause.sentence.length - 1; i += 1) {
    const word = clause.sentence[i];
    const wclass = spanMaps.spanMap[i];
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
      currentSpan = { wclass, mclass: spanMaps.spanMap2[i], words: [word] };
    }
  }
  if (currentSpan.words) {
    currentSpan.idx = spans.length;
    currentSpan.title = SPAN_TITLES[currentSpan.wclass];
    if (currentSpan.title) currentSpan.cclass = 'help';
    currentSpan.words = currentSpan.words.join(' ');
    spans.push(currentSpan);
  }
  return spans;
}

function controller($scope, $rootScope, $routeParams, $location, Clauses) {
  // make the call to the REST API to fetch the clause object
  $scope.spans = [];
  $scope.annotation = {};
  Clauses.get({ id: $routeParams.clauseId },
              (clause) => {
                $scope.spans = getSpans(clause);
                if (!Clauses.cache.clause.annotation) {
                  Clauses.cache.clause.annotation = {
                    invalid: 'uncertain',
                    stative: 'uncertain',
                    bounded: 'uncertain',
                    extended: 'uncertain',
                    change: 'uncertain'
                  };
                }
                $scope.annotation = Clauses.cache.clause.annotation;
              },
              () => { location = '/annotations/'; });
  // we use the Clause service's cache to access the clause
  // object in the page
  $scope.cached = Clauses.cache;
  $scope.isClean = Clauses.isClean;
  $scope.save = Clauses.save;

  this.invalidChanged = () => {
    if ($scope.annotation.invalid == 'true') {
      $scope.annotation.stative = 'uncertain';
      $scope.annotation.bounded = 'uncertain';
      $scope.annotation.extended = 'uncertain';
      $scope.annotation.change = 'uncertain';
    }
  };
  this.stativeChanged = () => {
    if ($scope.annotation.stative == 'true') {
      $scope.annotation.bounded = 'false';
      $scope.annotation.extended = 'false';
      $scope.annotation.change = 'false';
    }
  };
  this.boundedChanged = () => {
    if ($scope.annotation.bounded == 'false') {
      /* maybe set change to FALSE? */
    }
  };
  this.extendedChanged = () => {
    // nothing to do here
  };
  this.changeChanged = () => {
    // nothing to do here
  };
  this.shouldSave = () =>
    (Clauses.cache.original &&
     !Clauses.isClean() &&
     !(Clauses.cache.clause.annotation.invalid == 'uncertain' &&
       Clauses.cache.clause.annotation.stative == 'uncertain' &&
       Clauses.cache.clause.annotation.bounded == 'uncertain' &&
       Clauses.cache.clause.annotation.extended == 'uncertain' &&
       Clauses.cache.clause.annotation.change == 'uncertain'));
  this.left = () => {
    if (Clauses.cache.clause && Clauses.cache.clause.id !== 1) {
      const newUrl = `/${Clauses.cache.clause.id - 1}`;
      if (this.shouldSave()) {
        Clauses.save(() => {
          $location.url(newUrl);
        });
      } else {
        $location.url(newUrl);
      }
    }
  };
  this.right = () => {
    if (Clauses.cache.clause && !Clauses.cache.clause.last) {
      const newUrl = `/${Clauses.cache.clause.id + 1}`;
      if (this.shouldSave()) {
        Clauses.save(() => {
          $location.url(newUrl);
        });
      } else {
        $location.url(newUrl);
      }
    }
  };
  this.keyDown = (broadcast, event) => {
    //console.log('keyDown');
    //console.log(event); /* key event is here */
    if (event.which == 37) {
      $rootScope.$evalAsync(() => { this.left(); });   // left
    }
    if (event.which == 39) {
      $rootScope.$evalAsync(() => { this.right(); });  // right
    }
    // event.which === 73 // i
    // event.which === 86 // v
    // event.which === 83 // s
    // event.which === 68 // d
    // event.which === 85 // u
    // event.which === 66 // b
    // event.which === 67 // c
    // event.which === 78 // n
  }
  $rootScope.$on('bodySendsKeyDown', this.keyDown);
}

export default {
  restrict: 'E',
  controller,
  template,
};
