import { describe, expect, it } from 'vitest';
import {
  BANCO_TRIVIA,
  PREGUNTAS_POR_RONDA,
  crearEstadoTrivia,
  iniciarRonda,
  preguntaActual,
  responderEnTrivia,
  avanzarEnTrivia,
} from './trivia.js';

const semilla = 20261120;

describe('Trivia del Desafío Verde (REC-162)', () => {
  it('tiene al menos 20 preguntas con respuesta y explicación', () => {
    expect(BANCO_TRIVIA.length).toBeGreaterThanOrEqual(20);
    for (const p of BANCO_TRIVIA) {
      expect(p.id).toBeTruthy();
      expect(p.pregunta).toBeTruthy();
      expect(p.opciones).toHaveLength(3);
      expect(p.correcta).toBeGreaterThanOrEqual(0);
      expect(p.correcta).toBeLessThan(3);
      expect(p.explicacion).toBeTruthy();
      expect(p.fuente).toBeTruthy();
    }
  });

  it('el orden es aleatorio pero reproducible con la misma semilla', () => {
    const a = crearEstadoTrivia({ semilla: 7 }).ronda.map((p) => p.id);
    const b = crearEstadoTrivia({ semilla: 7 }).ronda.map((p) => p.id);
    expect(a).toEqual(b);
    expect(crearEstadoTrivia({ semilla: 8 }).ronda.map((p) => p.id)).not.toEqual(a);
  });

  it('una ronda toma 5 preguntas distintas', () => {
    const estado = crearEstadoTrivia({ semilla });
    expect(estado.ronda).toHaveLength(PREGUNTAS_POR_RONDA);
    const ids = estado.ronda.map((p) => p.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it('dos rondas consecutivas no son idénticas y priorizan no vistas', () => {
    const primera = crearEstadoTrivia({ semilla });
    const idsPrimera = primera.ronda.map((p) => p.id);
    const segunda = iniciarRonda(primera);
    const idsSegunda = segunda.ronda.map((p) => p.id);
    expect(idsSegunda).not.toEqual(idsPrimera);
    expect(idsSegunda.filter((id) => idsPrimera.includes(id))).toHaveLength(0);
    expect(segunda.vistas.length).toBe(PREGUNTAS_POR_RONDA * 2);
  });

  it('al agotar el banco se reinicia sin error', () => {
    let estado = crearEstadoTrivia({ semilla });
    const vistas = new Set();

    for (let ronda = 0; ronda < BANCO_TRIVIA.length / PREGUNTAS_POR_RONDA; ronda++) {
      estado.ronda.forEach((p) => vistas.add(p.id));
      if (ronda < BANCO_TRIVIA.length / PREGUNTAS_POR_RONDA - 1) {
        estado = iniciarRonda(estado);
      }
    }

    expect(vistas.size).toBe(BANCO_TRIVIA.length);
    expect(estado.vistas.length).toBe(BANCO_TRIVIA.length);
    const ciclosAntes = estado.ciclos;
    const siguiente = iniciarRonda(estado);
    expect(siguiente.ciclos).toBe(ciclosAntes + 1);
    expect(siguiente.vistas).toHaveLength(PREGUNTAS_POR_RONDA);
    expect(new Set(siguiente.ronda.map((p) => p.id)).size).toBe(PREGUNTAS_POR_RONDA);
  });

  it('el puntaje es correcto y la ronda termina con puntaje', () => {
    let estado = crearEstadoTrivia({ semilla });
    expect(avanzarEnTrivia(estado)).toBe(estado); // no avanza sin responder
    const primera = preguntaActual(estado);
    estado = responderEnTrivia(estado, primera.correcta);
    estado = avanzarEnTrivia(estado);

    const segunda = preguntaActual(estado);
    const incorrecta = (segunda.correcta + 1) % segunda.opciones.length;
    estado = responderEnTrivia(estado, incorrecta);
    expect(estado.respondidas).toBe(2);
    expect(estado.aciertos).toBe(1);

    // No se puede responder dos veces la misma pregunta.
    const duplicada = responderEnTrivia(estado, segunda.correcta);
    expect(duplicada).toBe(estado);
    estado = avanzarEnTrivia(estado);
    expect(estado.indice).toBe(2);

    for (let i = 2; i < PREGUNTAS_POR_RONDA; i++) {
      estado = responderEnTrivia(estado, preguntaActual(estado).correcta);
      estado = avanzarEnTrivia(estado);
    }
    expect(estado.terminada).toBe(true);
    expect(estado.respondidas).toBe(PREGUNTAS_POR_RONDA);
    expect(estado.aciertos).toBe(PREGUNTAS_POR_RONDA - 1);
  });
});
