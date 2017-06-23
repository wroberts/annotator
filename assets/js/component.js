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
  clause['aspectual-indicators'].forEach((comp) => {
    for (let i = comp.begin; i < comp.end; i += 1) {
      spanMap[i] = comp.type;
      spanMap2[i] = 'aspind';
    }
  });
  clause['verb-comps'].forEach((comp) => {
    for (let i = comp.begin; i < comp.end; i += 1) {
      spanMap[i] = comp.type;
      spanMap2[i] = 'synarg';
    }
  });
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

function initAnnotation(clause, $scope) {
  if (!clause.annotation) {
    clause.annotation = {
      invalid: 'uncertain',
      stative: 'uncertain',
      bounded: 'uncertain',
      extended: 'uncertain',
      change: 'uncertain',
    };
  }
  $scope.annotation = clause.annotation;
}

function controller($scope, $rootScope, $routeParams, $location, Clauses) {
  // make the call to the REST API to fetch the clause object
  $scope.spans = [];
  $scope.annotation = {};
  Clauses.get({ id: $routeParams.clauseId },
              (clause) => {
                $scope.spans = getSpans(clause);
                initAnnotation(Clauses.cache.clause, $scope);
              },
              () => { location.href = '/annotations/'; });
  // we use the Clause service's cache to access the clause
  // object in the page
  $scope.cached = Clauses.cache;
  $scope.isClean = Clauses.isClean;
  $scope.save = Clauses.save;

  this.reset = () => {
    Clauses.cache.clause = angular.copy(Clauses.cache.original);
    initAnnotation(Clauses.cache.clause, $scope);
  };
  $scope.reset = this.reset;
  this.invalidChanged = () => {
    if ($scope.annotation.invalid === 'true') {
      $scope.annotation.stative = 'uncertain';
      $scope.annotation.bounded = 'uncertain';
      $scope.annotation.extended = 'uncertain';
      $scope.annotation.change = 'uncertain';
    }
  };
  this.stativeChanged = () => {
    if ($scope.annotation.stative === 'false' || $scope.annotation.stative === 'true') {
      $scope.annotation.invalid = 'false';
    }
    if ($scope.annotation.stative === 'true') {
      $scope.annotation.bounded = 'false';
      $scope.annotation.extended = 'true';
      $scope.annotation.change = 'false';
    }
  };
  this.boundedChanged = () => {
    if ($scope.annotation.bounded === 'false' || $scope.annotation.bounded === 'true') {
      $scope.annotation.invalid = 'false';
      $scope.annotation.stative = 'false';
    }
    if ($scope.annotation.bounded === 'false') {
      $scope.annotation.extended = 'true';
      $scope.annotation.change = 'false';
    }
  };
  this.extendedChanged = () => {
    if ($scope.annotation.extended === 'false' || $scope.annotation.extended === 'true') {
      $scope.annotation.invalid = 'false';
      $scope.annotation.stative = 'false';
      $scope.annotation.bounded = 'true';
    }
  };
  this.changeChanged = () => {
    if ($scope.annotation.change === 'false' || $scope.annotation.change === 'true') {
      $scope.annotation.invalid = 'false';
      $scope.annotation.stative = 'false';
      $scope.annotation.bounded = 'true';
    }
  };
  this.shouldSave = () =>
    (Clauses.cache.original &&
     !Clauses.isClean() &&
     !(Clauses.cache.clause.annotation.invalid === 'uncertain' &&
       Clauses.cache.clause.annotation.stative === 'uncertain' &&
       Clauses.cache.clause.annotation.bounded === 'uncertain' &&
       Clauses.cache.clause.annotation.extended === 'uncertain' &&
       Clauses.cache.clause.annotation.change === 'uncertain'));
  $scope.shouldSave = this.shouldSave;
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
  this.keyDown = (event) => {
    // console.log('keyDown');
    // console.log(event); /* key event is here */
    if (Clauses.cache.clause) {
      if (event.which === 37) {
        this.left();   // left
      }
      if (event.which === 39) {
        this.right();  // right
      }
      if (event.which === 27) {
        this.reset();  // ESCAPE
      }
      if (event.which === 73) {
        // i
        $scope.annotation.invalid = 'true';
        this.invalidChanged();
      }
      if (event.which === 86) {
        // v
        $scope.annotation.invalid = 'false';
        this.invalidChanged();
      }
      if (event.which === 83) {
        // s
        $scope.annotation.stative = 'true';
        this.stativeChanged();
      }
      if (event.which === 68) {
        // d
        $scope.annotation.stative = 'false';
        this.stativeChanged();
      }
      if (event.which === 85) {
        // u
        $scope.annotation.bounded = 'false';
        this.boundedChanged();
      }
      if (event.which === 66) {
        // b
        $scope.annotation.bounded = 'true';
        this.boundedChanged();
      }
      if (event.which === 69) {
        // e
        $scope.annotation.extended = 'true';
        this.extendedChanged();
      }
      if (event.which === 80) {
        // p
        $scope.annotation.extended = 'false';
        this.extendedChanged();
      }
      if (event.which === 67) {
        // c
        $scope.annotation.change = 'true';
        this.changeChanged();
      }
      if (event.which === 78) {
        // n
        $scope.annotation.change = 'false';
        this.changeChanged();
      }
    }
  };
  $rootScope.$on('bodySendsKeyDown',
                 (broadcastEvt, keyEvt) => {
                   $rootScope.$evalAsync(() => { this.keyDown(keyEvt); });
                 });
}

export default {
  restrict: 'E',
  controller,
  template,
};
