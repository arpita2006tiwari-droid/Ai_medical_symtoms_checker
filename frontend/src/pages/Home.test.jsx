import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import '@testing-library/jest-dom';
import Home from './Home';
import * as AuthContextModule from '../context/AuthContext';

// Mock the AuthContext hook
vi.mock('../context/AuthContext', async () => {
  const actual = await vi.importActual('../context/AuthContext');
  return {
    ...actual,
    useAuth: vi.fn(),
  };
});

const renderWithRouter = (ui) => {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
};

describe('Home Component', () => {
  it('renders loading state without flashing unauthenticated buttons', () => {
    vi.mocked(AuthContextModule.useAuth).mockReturnValue({
      user: null,
      loading: true,
    });

    renderWithRouter(<Home />);
    
    // Buttons should not be present
    expect(screen.queryByText(/Check Symptoms/i)).toBeNull();
    expect(screen.queryByText(/Log In/i)).toBeNull();
    expect(screen.queryByText(/Go to Dashboard/i)).toBeNull();
  });

  it('renders unauthenticated state with Check Symptoms and Log In buttons', () => {
    vi.mocked(AuthContextModule.useAuth).mockReturnValue({
      user: null,
      loading: false,
    });

    renderWithRouter(<Home />);
    
    expect(screen.getByText(/Check Symptoms/i)).toBeInTheDocument();
    expect(screen.getByText(/Log In/i)).toBeInTheDocument();
    
    expect(screen.queryByText(/Go to Dashboard/i)).toBeNull();
  });

  it('renders authenticated state with Dashboard and Check Symptoms buttons', () => {
    vi.mocked(AuthContextModule.useAuth).mockReturnValue({
      user: { email: 'test@example.com', full_name: 'Test User' },
      loading: false,
    });

    renderWithRouter(<Home />);
    
    expect(screen.getByText(/Go to Dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/Check Symptoms/i)).toBeInTheDocument();
    
    expect(screen.queryByText(/Log In/i)).toBeNull();
  });
});
