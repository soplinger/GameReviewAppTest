import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ReviewForm } from './ReviewForm';

describe('ReviewForm', () => {
  const mockOnSubmit = vi.fn();
  const mockOnCancel = vi.fn();

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders all form fields', () => {
    render(
      <ReviewForm gameId={1} onSubmit={mockOnSubmit} onCancel={mockOnCancel} />
    );

    expect(screen.getByText(/rating/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/review title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/review content/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/playtime/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/platform/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/recommend/i)).toBeInTheDocument();
  });

  it('displays star rating selector', () => {
    render(<ReviewForm gameId={1} onSubmit={mockOnSubmit} />);

    const stars = screen.getAllByRole('button', { name: '' });
    // Should have 5 star buttons
    expect(stars.length).toBeGreaterThanOrEqual(5);
  });

  it('validates minimum rating requirement', async () => {
    render(<ReviewForm gameId={1} onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/review title/i);
    const contentInput = screen.getByLabelText(/review content/i);
    const submitButton = screen.getByRole('button', { name: /publish review/i });

    fireEvent.change(titleInput, { target: { value: 'Great Game' } });
    fireEvent.change(contentInput, {
      target: { value: 'This is a great game with lots of content. '.repeat(3) },
    });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/please select a rating/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('validates minimum title length', async () => {
    render(<ReviewForm gameId={1} onSubmit={mockOnSubmit} />);

    const stars = screen.getAllByRole('button', { name: '' });
    fireEvent.click(stars[3]); // Select 4 stars

    const titleInput = screen.getByLabelText(/review title/i);
    const contentInput = screen.getByLabelText(/review content/i);
    const submitButton = screen.getByRole('button', { name: /publish review/i });

    fireEvent.change(titleInput, { target: { value: 'OK' } }); // Too short
    fireEvent.change(contentInput, {
      target: { value: 'This is a great game with lots of content. '.repeat(3) },
    });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/title must be at least 5 characters/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('validates minimum content length', async () => {
    render(<ReviewForm gameId={1} onSubmit={mockOnSubmit} />);

    const stars = screen.getAllByRole('button', { name: '' });
    fireEvent.click(stars[3]); // Select 4 stars

    const titleInput = screen.getByLabelText(/review title/i);
    const contentInput = screen.getByLabelText(/review content/i);
    const submitButton = screen.getByRole('button', { name: /publish review/i });

    fireEvent.change(titleInput, { target: { value: 'Great Game' } });
    fireEvent.change(contentInput, { target: { value: 'Too short' } });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText(/review content must be at least 50 characters/i)
      ).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('submits valid review data', async () => {
    mockOnSubmit.mockResolvedValue(undefined);

    render(<ReviewForm gameId={1} onSubmit={mockOnSubmit} />);

    const stars = screen.getAllByRole('button', { name: '' });
    fireEvent.click(stars[3]); // Select 4 stars

    const titleInput = screen.getByLabelText(/review title/i);
    const contentInput = screen.getByLabelText(/review content/i);
    const playtimeInput = screen.getByLabelText(/playtime/i);
    const platformInput = screen.getByLabelText(/platform/i);
    const submitButton = screen.getByRole('button', { name: /publish review/i });

    fireEvent.change(titleInput, { target: { value: 'Excellent Game!' } });
    fireEvent.change(contentInput, {
      target: { value: 'This is an excellent game with amazing gameplay. '.repeat(3) },
    });
    fireEvent.change(playtimeInput, { target: { value: '25.5' } });
    fireEvent.change(platformInput, { target: { value: 'PC' } });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          game_id: 1,
          rating: 4,
          title: 'Excellent Game!',
          playtime_hours: 25.5,
          platform: 'PC',
          is_recommended: true,
        })
      );
    });
  });

  it('calls onCancel when cancel button is clicked', () => {
    render(<ReviewForm gameId={1} onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalled();
  });

  it('populates form with initial data when editing', () => {
    const initialData = {
      rating: 4,
      title: 'Great Game',
      content: 'This is a great game with lots of fun gameplay mechanics. '.repeat(2),
      playtime_hours: 25,
      platform: 'PlayStation 5',
      is_recommended: true,
    };

    render(
      <ReviewForm
        gameId={1}
        initialData={initialData}
        onSubmit={mockOnSubmit}
        isEditing={true}
      />
    );

    const titleInput = screen.getByLabelText(/review title/i) as HTMLInputElement;
    const contentInput = screen.getByLabelText(/review content/i) as HTMLTextAreaElement;
    const playtimeInput = screen.getByLabelText(/playtime/i) as HTMLInputElement;
    const platformInput = screen.getByLabelText(/platform/i) as HTMLInputElement;

    expect(titleInput.value).toBe('Great Game');
    expect(contentInput.value).toContain('great game');
    expect(playtimeInput.value).toBe('25');
    expect(platformInput.value).toBe('PlayStation 5');
  });

  it('shows update button text when editing', () => {
    render(
      <ReviewForm gameId={1} onSubmit={mockOnSubmit} isEditing={true} />
    );

    expect(screen.getByRole('button', { name: /update review/i })).toBeInTheDocument();
  });

  it('displays character count for content', () => {
    render(<ReviewForm gameId={1} onSubmit={mockOnSubmit} />);

    const contentInput = screen.getByLabelText(/review content/i);

    expect(screen.getByText(/0 \/ 50 characters minimum/i)).toBeInTheDocument();

    fireEvent.change(contentInput, {
      target: { value: 'Testing content length counter with some text here' },
    });

    expect(screen.getByText(/51 \/ 50 characters minimum/i)).toBeInTheDocument();
  });
});
