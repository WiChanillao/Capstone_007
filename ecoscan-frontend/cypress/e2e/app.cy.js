/// <reference types="cypress" />

describe('EcoLearn Chile - app funcional', () => {
  it('muestra las 5 pestañas y el simulador sin controles manuales', () => {
    cy.visit('/');
    cy.contains('EcoLearn Chile').should('be.visible');
    cy.get('nav button').should('have.length', 5);

    cy.contains('button', 'Eco-Simulador RM').click();
    cy.contains('Residuos detectados por IA').should('be.visible');
    cy.get('input[type="range"]').should('not.exist');
    cy.contains('Guardar escenario').should('not.exist');
    cy.contains('Escaneos reales:').should('be.visible');
  });

  it('ordena puntos por cercanía con geolocalización autorizada', () => {
    cy.visit('/');
    cy.window().then((win) => {
      win.navigator.geolocation.getCurrentPosition = (cb) =>
        cb({ coords: { latitude: -33.4489, longitude: -70.6693 } });
    });
    cy.contains('button', 'Puntos Limpios RM').click();
    cy.contains('button', 'Usar mi ubicación').click();
    cy.contains('puntos ordenados por cercanía').should('be.visible');
    cy.contains('A 3.2 km de tu ubicación').should('be.visible');
  });

  it('muestra el Desafío Verde con progreso automático', () => {
    cy.visit('/');
    cy.contains('button', 'Desafío Verde RM').click();
    cy.contains('Progreso').should('be.visible');
  });
});
