interface FormErrorProps {
  message?: string;
}

export function FormError({ message }: FormErrorProps) {
  if (!message) return null;

  return (
    <div className="border border-white/20 bg-black p-3 text-sm text-white flex items-center gap-x-2">
      <p>{message}</p>
    </div>
  );
}
