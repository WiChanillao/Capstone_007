import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import App from './App.jsx';

const impacto = {
  escaneos: 48,
  ventana_dias: 30,
  fuente: 'MySQL ecoscan.escaneos + item_simulador',
  materiales: { carton: 13, aluminio: 21, plastico: 13 },
  impacto: { agua_litros: 237, co2_kg: 7.86, residuos_kg: 2.27 },
  equivalencias: { duchas_5min: 4, km_auto: 59 },
  factores: {
    carton: { agua_litros: 12, co2_kg: 0.25, residuos_kg: 0.12 },
    aluminio: { agua_litros: 2, co2_kg: 0.17, residuos_kg: 0.015 },
    plastico: { agua_litros: 3, co2_kg: 0.08, residuos_kg: 0.03 },
  },
};

beforeEach(() => {
  localStorage.clear();
  vi.stubGlobal('fetch', vi.fn(async (url) => {
    const u = String(url);
    let datos = [];
    if (u.includes('/db/impacto')) datos = impacto;
    else if (u.includes('/db/sesiones')) datos = { id_sesion: 'sesion-unitaria' };
    else if (u.includes('/predict')) datos = { detecciones: [{ clase: 'plastico', confianza: 0.9 }] };
    return { ok: true, status: 200, json: async () => datos };
  }));
});

describe('EcoLearn Chile (App)', () => {
  it('muestra exactamente las 5 pestañas permitidas', () => {
    render(<App />);
    const nombres = screen.getAllByRole('button').map((b) => b.textContent || '');
    for (const pestaña of ['Menú Principal', 'Escáner IA', 'Puntos Limpios RM',
                           'Eco-Simulador RM', 'Desafío Verde RM']) {
      expect(nombres.some((n) => n.includes(pestaña))).toBe(true);
    }
  });

  it('no contiene sliders ni controles manuales de simulación', () => {
    const { container } = render(<App />);
    expect(container.querySelectorAll('input[type="range"]')).toHaveLength(0);
    expect(container.querySelectorAll('input[type="number"]')).toHaveLength(0);
  });

  it('toma el impacto desde MySQL y lo muestra en el simulador', async () => {
    render(<App />);
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/db/impacto?id_sesion='));
    });
    fireEvent.click(screen.getByRole('button', { name: /Eco-Simulador RM/ }));
    expect(await screen.findByText(/Residuos detectados por IA/)).toBeInTheDocument();
    expect(screen.getByText(/No hay controles manuales/)).toBeInTheDocument();
  });

  it('muestra los valores reales calculados desde la base de datos', async () => {
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /Eco-Simulador RM/ }));
    expect(await screen.findByText(/237 L/)).toBeInTheDocument();
  });

  it('muestra videos de reutilización por material y los abre sin autoplay', async () => {
    const { container } = render(<App />);
    fireEvent.click(screen.getAllByRole('button', { name: /Escáner IA/ })[0]);
    const input = container.querySelector('input[type="file"]');
    expect(input).not.toBeNull();
    fireEvent.change(input, {
      target: { files: [new File(['foto'], 'botella.jpg', { type: 'image/jpeg' })] },
    });
    expect(await screen.findByText(/Materiales Identificados/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /¿Cómo Reutilizar\?/ }));
    expect(screen.getByTestId('videos-reutilizar-plastico')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Ver video: 3 ideas con botellas/ })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Ver video: 3 ideas con botellas/ }));
    const modal = await screen.findByRole('dialog', { name: /3 ideas con botellas/ });
    const iframe = modal.querySelector('iframe');
    expect(iframe.getAttribute('src')).toContain('lhhggoTyiPY');
    expect(iframe.getAttribute('src')).not.toContain('autoplay');
  });
});
