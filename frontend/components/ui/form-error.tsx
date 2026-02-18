interface FormErrorProps {
  message?: string;
}

export function FormError({ message }: FormErrorProps) {
  if (!message) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-500 flex items-center gap-x-2">
      <p>{message}</p>
    </div>
  );
}
